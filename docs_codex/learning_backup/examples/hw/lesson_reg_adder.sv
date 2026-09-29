// Original standalone teaching example. Not instantiated in Cheshire.
// Byte-addressed 32-bit Reg-like interface; no AXI burst, queues or CDC.
module lesson_reg_adder (
  input logic clk_i, rst_ni,
  input logic valid_i, write_i,
  input logic [31:0] addr_i, wdata_i,
  input logic [3:0] wstrb_i,
  output logic ready_o, error_o,
  output logic [31:0] rdata_o,
  output logic irq_o
);
  logic [31:0] a_q, b_q, result_q, pending_q;
  logic busy_q, done_q, irq_en_q;
  logic [2:0] ticks_q;
  assign ready_o = valid_i;
  assign irq_o = done_q & irq_en_q;
  always_comb begin
    error_o = 1'b0;
    rdata_o = '0;
    case (addr_i)
      32'h00: begin rdata_o = a_q; if (write_i && busy_q) error_o = 1; end
      32'h04: begin rdata_o = b_q; if (write_i && busy_q) error_o = 1; end
      32'h08: if (write_i && wstrb_i[0] && wdata_i[0] && (busy_q || done_q)) error_o = 1;
      32'h0c: rdata_o = {30'b0, done_q, busy_q};
      32'h10: begin rdata_o = result_q; if (write_i) error_o = 1; end
      32'h14: rdata_o = {31'b0, irq_en_q};
      default: error_o = 1;
    endcase
    if (!valid_i) error_o = 0;
  end
  always_ff @(posedge clk_i or negedge rst_ni) begin
    if (!rst_ni) begin
      a_q <= 0; b_q <= 0; result_q <= 0; pending_q <= 0;
      busy_q <= 0; done_q <= 0; irq_en_q <= 0; ticks_q <= 0;
    end else begin
      if (valid_i && ready_o && write_i && !error_o) begin
        case (addr_i)
          32'h00: for (int j=0;j<4;j++) if (wstrb_i[j]) a_q[j*8+:8] <= wdata_i[j*8+:8];
          32'h04: for (int j=0;j<4;j++) if (wstrb_i[j]) b_q[j*8+:8] <= wdata_i[j*8+:8];
          32'h08: if (wstrb_i[0] && wdata_i[0]) begin // START snapshots operands.
            pending_q <= a_q + b_q; busy_q <= 1; ticks_q <= 4;
          end
          32'h0c: if (wstrb_i[0] && wdata_i[1]) done_q <= 0; // W1C
          32'h14: if (wstrb_i[0]) irq_en_q <= wdata_i[0];
          default: ;
        endcase
      end
      if (busy_q) begin
        ticks_q <= ticks_q - 1'b1;
        if (ticks_q == 1) begin
          result_q <= pending_q; busy_q <= 0;
          done_q <= 1; // Hardware set wins over simultaneous W1C.
        end
      end
    end
  end
endmodule
