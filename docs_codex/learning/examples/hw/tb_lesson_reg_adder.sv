`timescale 1ns/1ps
module tb_lesson_reg_adder;
  logic clk=0, rst=0, valid=0, wr=0;
  logic [31:0] addr=0, wd=0, rd;
  logic [3:0] strb=0;
  logic ready, err, irq;
  logic [31:0] got;
  integer checks=0;
  always #5 clk=~clk;
  lesson_reg_adder dut(clk,rst,valid,wr,addr,wd,strb,ready,err,rd,irq);
  task automatic check(input bit ok,input string label_text);
    if (!ok) $fatal(1,"HW_UNIT_FAIL %s time=%0t",label_text,$time);
    checks++;
  endtask
  task automatic access_reg(input bit write_en,input logic[31:0] offset,data,
      input logic[3:0] mask,input bit expected_error,output logic[31:0] result);
    @(negedge clk);valid=1;wr=write_en;addr=offset;wd=data;strb=mask;
    #1;check(ready && err==expected_error,"access ready/error");result=rd;
    @(posedge clk);#1;
    @(negedge clk);valid=0;
  endtask
  initial begin
    repeat(2) @(negedge clk);rst=1;
    access_reg(0,'h0c,0,0,0,got);check(got==0 && !irq,"reset state");
    access_reg(1,0,'h11223344,4'hf,0,got);
    access_reg(1,0,'h0000aa00,4'h2,0,got);
    access_reg(0,0,0,0,0,got);check(got=='h1122aa44,"byte strobe");
    access_reg(1,0,0,0,0,got);
    access_reg(0,0,0,0,0,got);check(got=='h1122aa44,"zero strobe");
    access_reg(1,4,5,4'hf,0,got);
    access_reg(1,'h14,1,1,0,got);
    access_reg(1,8,1,1,0,got);check(dut.busy_q,"start busy");
    access_reg(1,8,1,1,1,got); // Still busy; must reject.
    repeat(6) @(negedge clk);
    access_reg(0,'h10,0,0,0,got);check(got=='h1122aa49 && irq,"result and IRQ");
    access_reg(1,8,1,1,1,got); // DONE not cleared.
    access_reg(1,'h0c,2,0,0,got);check(irq,"W1C needs byte enable");
    access_reg(1,'h0c,2,1,0,got);check(!irq,"clear done clears IRQ");
    access_reg(1,'h10,9,15,1,got);
    access_reg(0,2,0,0,1,got);
    access_reg(0,'h18,0,0,1,got);
    // Overflow is explicitly modulo 2^32; masked DONE remains readable.
    access_reg(1,'h14,0,1,0,got);
    access_reg(1,0,'hffffffff,15,0,got);
    access_reg(1,4,1,15,0,got);
    access_reg(1,8,1,1,0,got);
    // Exercise same-cycle hardware set versus software clear, tied to this unit's latency.
    wait(dut.busy_q && dut.ticks_q==1);
    @(negedge clk);valid=1;wr=1;addr='h0c;wd=2;strb=1;
    @(posedge clk);#1;check(dut.done_q,"hardware set wins W1C");
    @(negedge clk);valid=0;
    access_reg(0,'h10,0,0,0,got);check(got==0 && !irq,"modulo result and IRQ mask");
    access_reg(0,'h0c,0,0,0,got);check(got==2,"DONE readable while masked");
    // A request with valid=0 must not write operands.
    @(negedge clk);valid=0;wr=1;addr=0;wd=123;strb=15;
    repeat(2) @(negedge clk);
    access_reg(0,0,0,0,0,got);check(got=='hffffffff,"no valid no write");
    if ($test$plusargs("INJECT_FAIL")) check(0,"injected checker failure");
    $display("HW_UNIT_PASS checks=%0d",checks);$finish;
  end
  initial begin #10000;$fatal(1,"HW_UNIT_FAIL timeout");end
endmodule
