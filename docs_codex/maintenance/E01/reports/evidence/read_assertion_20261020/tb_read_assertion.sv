`timescale 1ns/1ps
module tb_read_assertion;
  function automatic config_pkg::cva6_cfg_t make_cfg();
    config_pkg::cva6_cfg_t c=config_pkg::cva6_cfg_empty;
    c.XLEN=64;c.XLEN_ALIGN_BYTES=3;c.PLEN=56;c.DCACHE_INDEX_WIDTH=12;
    c.DCACHE_OFFSET_WIDTH=6;c.DCACHE_TAG_WIDTH=44;c.DCACHE_SET_ASSOC=4;
    c.DCACHE_USER_WIDTH=1;c.DcacheIdWidth=2;c.MEM_TID_WIDTH=2;
    return c;
  endfunction
  localparam config_pkg::cva6_cfg_t Cfg=make_cfg();
  typedef struct packed {
    logic [43:0] address_tag;logic [11:0] address_index;
    logic data_req,kill_req,tag_valid;logic [1:0] data_size,data_id;
  } request_t;
  typedef struct packed {
    logic data_rvalid,data_gnt;logic [63:0] data_rdata;
    logic data_ruser;logic [1:0] data_rid;
  } response_t;
  logic clk=0,rst=0;always #5 clk=~clk;
  request_t req;response_t rsp;
  logic ack=1,miss_ack=0,miss_return=0,miss_replay=0,wr_cl=0;
  logic [3:0] hit=1;logic [63:0] data;
  wt_dcache_ctrl #(.CVA6Cfg(Cfg),.DCACHE_CL_IDX_WIDTH(6),
    .dcache_req_i_t(request_t),.dcache_req_o_t(response_t)) dut (
    .clk_i(clk),.rst_ni(rst),.cache_en_i(1'b1),.busy_o(),.stall_i(1'b0),
    .req_port_i(req),.req_port_o(rsp),.miss_req_o(),.miss_ack_i(miss_ack),
    .miss_we_o(),.miss_wdata_o(),.miss_wuser_o(),.miss_vld_bits_o(),
    .miss_paddr_o(),.miss_nc_o(),.miss_size_o(),.miss_id_o(),
    .miss_replay_i(miss_replay),.miss_rtrn_vld_i(miss_return),.wr_cl_vld_i(wr_cl),
    .rd_tag_o(),.rd_idx_o(),.rd_off_o(),.rd_req_o(),.rd_tag_only_o(),
    .rd_ack_i(ack),.rd_data_i(data),.rd_user_i(1'b0),.rd_vld_bits_i(4'hf),.rd_hit_oh_i(hit));
  int cases=0;
  task automatic reset_dut();
    @(negedge clk);rst=0;req='0;data='x;hit=1;ack=1;
    miss_ack=0;miss_return=0;miss_replay=0;wr_cl=0;
    repeat(2) @(negedge clk);rst=1;
  endtask
  task automatic run_case(string label_,int off,logic [1:0] size_,logic [63:0] word_,
                          int expect_data,int expect_meta=0,bit kill_=0,int path_=0,
                          bit change_after_sample=0);
    reset_dut();cases++;
    @(negedge clk);
    $display("CASE %0d %s DATA=%0d META=%0d WORD=%h",cases,label_,expect_data,expect_meta,word_);
    req.address_index=12'(off);req.data_size=size_;req.data_id=2'd1;
    req.data_req=1;req.tag_valid=1;hit=(path_==1)?0:1;
    #1;if(!rsp.data_gnt)$fatal(1,"request not granted");
    @(posedge clk);#1;
    @(negedge clk);req.data_req=0;req.address_index=12'(7-off);req.data_size=2'(3-size_);
    req.kill_req=kill_;data=word_;
    if(path_==1)begin // cache miss, saved metadata must survive waiting
      @(posedge clk);#1;@(negedge clk);miss_ack=1;
      @(posedge clk);#1;@(negedge clk);miss_ack=0;
      repeat(3) @(negedge clk);
      miss_return=1;
    end
    if(path_==2)begin // replay after a cache array collision
      wr_cl=1;@(posedge clk);#1;@(negedge clk);wr_cl=0;
      @(posedge clk);#1;@(negedge clk);
    end
    #1;if(!rsp.data_rvalid)$fatal(1,"response not valid for %s",label_);
    if(rsp.data_rid!==2'd1)$fatal(1,"wrong response ID");
    @(posedge clk);if(change_after_sample)data=64'hdeaddeaddeaddead;
    #1;@(negedge clk);req='0;miss_return=0;
    $display("ENDCASE %0d",cases);
  endtask
  task automatic pipeline_case();
    reset_dut();cases++;@(negedge clk);
    $display("CASE %0d back_to_back_width_change DATA=0 META=0 WORD=00000000xxxxxxxx",cases);
    req.data_req=1;req.tag_valid=1;req.address_index=4;req.data_size=2;req.data_id=1;
    #1;if(!rsp.data_gnt)$fatal(1,"first grant missing");@(posedge clk);#1;
    @(negedge clk);req.address_index=0;req.data_size=0;req.data_id=2;data=64'h00000000xxxxxxxx;
    #1;if(!rsp.data_rvalid || !rsp.data_gnt || rsp.data_rid!==1)$fatal(1,"overlap missing");
    @(posedge clk);#1;@(negedge clk);req.data_req=0;data=64'hxxxxxxxxxxxxxx5a;
    #1;if(!rsp.data_rvalid || rsp.data_rid!==2)$fatal(1,"second response missing");
    @(posedge clk);#1;@(negedge clk);req='0;$display("ENDCASE %0d",cases);
  endtask
  logic [63:0] test_word;
  initial begin
    for(int sz=0;sz<4;sz++)begin
      for(int off=0;off<8;off+=(1<<sz))begin
        test_word='x;
        for(int b=off;b<off+(1<<sz);b++)test_word[b*8+:8]=0;
        run_case($sformatf("unused_x_s%0d_o%0d",sz,off),off,2'(sz),test_word,0);
        test_word='1;test_word[off*8+:8]='x;
        run_case($sformatf("used_x_with_ones_s%0d_o%0d",sz,off),off,2'(sz),test_word,1);
        test_word='1;test_word[off*8+:8]='z;
        run_case($sformatf("used_z_s%0d_o%0d",sz,off),off,2'(sz),test_word,1);
      end
    end
    run_case("cancelled",4,2,'x,0,0,1);
    run_case("metadata_x",4,2'bxx,'1,0,1);
    run_case("invalid_range",4,3,'1,0,1);
    run_case("miss_unused_x",4,2,64'h00000000xxxxxxxx,0,0,0,1);
    run_case("miss_used_x",4,2,64'hffffffxxffffffff,1,0,0,1);
    run_case("replay_unused_x",4,2,64'h00000000xxxxxxxx,0,0,0,2);
    run_case("replay_used_x",4,2,64'hffffffxxffffffff,1,0,0,2);
    run_case("sampled_print",4,2,64'hffffffxxffffffff,1,0,0,0,1);
    pipeline_case();
    $display("UNIT_DONE cases=%0d",cases);$finish;
  end
endmodule
