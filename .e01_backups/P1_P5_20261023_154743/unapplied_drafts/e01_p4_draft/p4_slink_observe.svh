// E01 P4 local draft, NOT compiled or run.
// Insert/include INSIDE tb_cheshire_soc, before endmodule.
// Default off. Enable with +P4_SLINK_OBSERVE +P4_CASE=1 (through 6).
// This samples the real VIP source interface. No force, drive, delay, or DPI call.
// The existing VIP sends AW, then W, then waits for B before another write;
// this observer intentionally uses that one-outstanding-write contract.
`define P4_AX fix.vip.slink_mst_vip_dv

bit p4_obs_enabled = 0;
int unsigned p4_obs_case = 0;
int unsigned p4_aw_count = 0, p4_data_aw = 0, p4_app_aw = 0;
int unsigned p4_w_count = 0, p4_b_count = 0, p4_error_count = 0;
int unsigned p4_missing = 0, p4_bad_bytes = 0;
bit p4_first_error_printed = 0, p4_write_active = 0;
bit p4_aw_usable = 0, p4_launch_data = 0, p4_launch_seen = 0;
longint unsigned p4_aw_addr, p4_aligned_start;
int unsigned p4_beat_bytes, p4_expected_beats, p4_seen_beats;
logic [7:0] p4_written [longint unsigned];

function automatic void p4_obs_error(input string reason);
  p4_error_count++;
  if (!p4_first_error_printed) begin
    $display("[P4_OBS_ERR] %s", reason);
    p4_first_error_printed = 1;
  end
endfunction

function automatic void p4_check_byte(
  input longint unsigned addr, input logic [7:0] expected
);
  if (!p4_written.exists(addr)) begin
    p4_missing++;
    p4_obs_error($sformatf("payload/pad byte never written addr=%h want=%h", addr, expected));
  end else if (p4_written[addr] !== expected) begin
    p4_bad_bytes++;
    p4_obs_error($sformatf("last written byte mismatch addr=%h got=%h want=%h",
                         addr, p4_written[addr], expected));
  end
endfunction

function automatic void p4_check_payload(
  input longint unsigned addr, input int unsigned length, input int unsigned seed
);
  for (int unsigned i=0; i<length; i++)
    p4_check_byte(addr+i, 8'(1+(37*i+seed)%251));
endfunction

function automatic void p4_check_padding(input longint unsigned end_addr);
  longint unsigned aligned_end;
  aligned_end = (end_addr+7) & ~64'd7;
  for (longint unsigned a=end_addr; a<aligned_end; a++) p4_check_byte(a, 8'h00);
endfunction

initial begin
  p4_obs_enabled = $test$plusargs("P4_SLINK_OBSERVE");
  if (p4_obs_enabled) begin
    if (!$value$plusargs("P4_CASE=%d", p4_obs_case) || p4_obs_case<1 || p4_obs_case>6)
      p4_obs_error("require +P4_CASE=1..6 matching the ELF; results invalid");
    if ($bits(`P4_AX.w_data)!=64 || $bits(`P4_AX.w_strb)!=8)
      p4_obs_error("observer is limited to the current 64-bit SLINK AXI data bus");
    $display("[P4_OBS_BEGIN] case=%0d source=tb_cheshire_soc.fix.vip.slink_mst_vip_dv",
             p4_obs_case);
  end
end

always @(posedge fix.vip.clk) begin : p4_watch_real_handshakes
  longint unsigned last_byte, beat_start, bus_word_start, lane_addr;
  string kind;
  if (p4_obs_enabled && fix.vip.rst_n) begin
    if (`P4_AX.aw_valid && `P4_AX.aw_ready) begin
      p4_aw_count++;
      if (p4_write_active) p4_obs_error("overlapping AW violates this VIP's sequential write contract");
      p4_write_active = 1;
      p4_aw_usable = !$isunknown({`P4_AX.aw_addr, `P4_AX.aw_len,
                                  `P4_AX.aw_size, `P4_AX.aw_burst}) &&
                     (`P4_AX.aw_size<=3) && (`P4_AX.aw_burst==axi_pkg::BURST_INCR);
      p4_aw_addr = `P4_AX.aw_addr;
      p4_expected_beats = int'(`P4_AX.aw_len)+1; // AWLEN=0 means ONE beat.
      p4_seen_beats = 0;
      p4_launch_data = 0;
      kind = "OTHER";
      if (p4_aw_addr>=64'h10000000 && p4_aw_addr<64'h10003000) begin
        kind = "DATA";
        p4_data_aw++;
      end else if (p4_aw_addr>=64'h10004000 && p4_aw_addr<64'h1000c000) begin
        kind = "APP";
        p4_app_aw++;
      end
      $display("[P4_AW] %s addr=%h len=%0d beats=%0d size=%0d burst=%0d",
               kind, `P4_AX.aw_addr, `P4_AX.aw_len, p4_expected_beats,
               `P4_AX.aw_size, `P4_AX.aw_burst);
      if (!p4_aw_usable) begin
        p4_obs_error("unknown/unsupported AW fields; payload reconstruction invalid");
      end else begin
        p4_beat_bytes = 1 << `P4_AX.aw_size;
        p4_aligned_start = p4_aw_addr & ~(64'(p4_beat_bytes)-1);
        last_byte = p4_aligned_start + 64'(p4_expected_beats)*p4_beat_bytes - 1;
        if ((p4_aw_addr>>12)!=(last_byte>>12))
          p4_obs_error($sformatf("cross-4KiB burst %s first=%h last=%h",
                               kind, p4_aw_addr, last_byte));
        if ((kind=="DATA" || kind=="APP") && `P4_AX.aw_size!=3)
          p4_obs_error("ELF preload did not use the current full-width 8-byte beat");
      end
    end

    if (`P4_AX.w_valid && `P4_AX.w_ready) begin
      p4_w_count++;
      if (!p4_write_active) begin
        p4_obs_error("W handshake without a preceding AW in this sequential VIP");
      end else begin
        if (`P4_AX.w_last !== (p4_seen_beats==p4_expected_beats-1))
          p4_obs_error($sformatf("WLAST/AWLEN mismatch addr=%h beat=%0d expected=%0d",
                               p4_aw_addr, p4_seen_beats, p4_expected_beats));
        if (p4_seen_beats>=p4_expected_beats) p4_obs_error("too many W handshakes for AWLEN");
        if (p4_seen_beats==0 || p4_seen_beats==p4_expected_beats-1)
          $display("[P4_W] aw=%h beat=%0d data=%h strb=%h last=%b",
                   p4_aw_addr, p4_seen_beats, `P4_AX.w_data, `P4_AX.w_strb, `P4_AX.w_last);
        if (p4_aw_usable) begin
          beat_start = p4_aligned_start + 64'(p4_seen_beats)*p4_beat_bytes;
          bus_word_start = beat_start & ~64'd7;
          for (int unsigned lane=0; lane<8; lane++) begin
            lane_addr = bus_word_start+lane;
            if ($isunknown(`P4_AX.w_strb[lane])) p4_obs_error("unknown WSTRB");
            if (`P4_AX.w_strb[lane] === 1'b1) begin
              if (lane_addr<beat_start || lane_addr>=beat_start+p4_beat_bytes ||
                  (p4_seen_beats==0 && lane_addr<p4_aw_addr))
                p4_obs_error("WSTRB enables a byte outside the addressed beat");
              if (lane_addr>=64'h10000000 && lane_addr<64'h10003000)
                p4_written[lane_addr] = `P4_AX.w_data[8*lane +: 8];
            end
          end
          if (p4_aw_addr==(cheshire_pkg::AmRegs+
                            cheshire_reg_pkg::CHESHIRE_SCRATCH_2_OFFSET) &&
              p4_seen_beats==0 && `P4_AX.w_strb[3:0]===4'hf &&
              `P4_AX.w_data[31:0]===32'd2)
            p4_launch_data = 1;
        end
        p4_seen_beats++;
      end
    end

    if (`P4_AX.b_valid && `P4_AX.b_ready) begin
      p4_b_count++;
      if (!p4_write_active) p4_obs_error("B handshake without a pending write");
      if (p4_seen_beats!=p4_expected_beats) p4_obs_error("B returned before the expected W count");
      if (`P4_AX.b_resp !== axi_pkg::RESP_OKAY)
        p4_obs_error($sformatf("BRESP not OKAY addr=%h resp=%b", p4_aw_addr, `P4_AX.b_resp));
      if (p4_launch_data && `P4_AX.b_resp===axi_pkg::RESP_OKAY) p4_launch_seen = 1;
      $display("[P4_B] aw=%h received_w=%0d resp=%b", p4_aw_addr, p4_seen_beats, `P4_AX.b_resp);
      p4_write_active = 0;
    end
  end
end

final begin
  if (p4_obs_enabled) begin
    if (p4_write_active) p4_obs_error("simulation ended with an unfinished AXI write");
    // Compare the LAST real strobed write to each byte, after every section.
    // In case 6, later B legitimately overwrites A's temporary tail padding.
    case (p4_obs_case)
      1: p4_check_payload(64'h10000000,1024,17);
      2: p4_check_payload(64'h10000000,2048,17);
      3: begin p4_check_payload(64'h10000000,1031,17); p4_check_padding(64'h10000407); end
      4: begin p4_check_payload(64'h10000001,1024,17); p4_check_padding(64'h10000401); end
      5: p4_check_payload(64'h10000ff8,16,17);
      6: begin
        p4_check_payload(64'h10002000,13,17);
        p4_check_payload(64'h1000200d,9,101);
        p4_check_padding(64'h10002016);
      end
      default: ;
    endcase
    $display("[P4_OBS_DONE] case=%0d aw=%0d data_aw=%0d app_aw=%0d w=%0d b=%0d missing=%0d bad=%0d errors=%0d launch=%0d",
             p4_obs_case,p4_aw_count,p4_data_aw,p4_app_aw,p4_w_count,p4_b_count,
             p4_missing,p4_bad_bytes,p4_error_count,p4_launch_seen);
    // Empty queue requests have no AW handshake. See the existing VIP fatal
    // (and optional read-only P4_OBS_EMPTY marker in README); never infer them
    // from AWLEN=0. This summary alone does not replace target result checking.
  end
end

`undef P4_AX
