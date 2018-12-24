/*
 *  A very basic test to make sure all states are exercized
 */

`timescale 1ns/100ps

module tb();
`ifndef D
    `define D #1
`endif

reg         clock;
reg         reset;
reg         next;
wire [7:0]  state;
wire [7:0]  state_next;

localparam
    stIDLE     = 0,
    stRED      = 1,
    stYELLOW   = 2,
    stGREEN    = 3,
    stMAGENTA  = 4,
    stBLUE     = 5,
    stWHITE    = 6,
    stBLACK    = 7;



initial begin
    $dumpfile("out.vcd");
    $dumpvars(0, tb);
end

initial begin
    clock = 1'b0;
    forever clock = #47 ~clock; // 16MHz
end

initial begin
    $display("==========================");
    $display(" Basic State Machine Test");
    $display("==========================");
    reset = 1'b1;
    next = 1'b0;

    #1;
    reset_chip;
    repeat(2) @(posedge clock);

    if(state[stIDLE] != 1'b1)
        $display("<%0t> Mismatch in stIDLE: %b", $time, state);
    else
        $display("<%0t> State: %b, Next: %b", $time, state, state_next);
    to_next_state;



    if(state[stRED] != 1'b1)
        $display("<%0t> Mismatch in stRED: %b", $time, state);
    else
        $display("<%0t> State: %b, Next: %b", $time, state, state_next);
    to_next_state;


    if(state[stYELLOW] != 1'b1)
        $display("<%0t> Mismatch in stYELLOW: %b", $time, state);
    else
        $display("<%0t> State: %b, Next: %b", $time, state, state_next);
    to_next_state;


    if(state[stGREEN] != 1'b1)
        $display("<%0t> Mismatch in stGREEN: %b", $time, state);
    else
        $display("<%0t> State: %b, Next: %b", $time, state, state_next);
    to_next_state;


    if(state[stMAGENTA] != 1'b1)
        $display("<%0t> Mismatch in stMAGENTA: %b", $time, state);
    else
        $display("<%0t> State: %b, Next: %b", $time, state, state_next);
    to_next_state;


    if(state[stBLUE] != 1'b1)
        $display("<%0t> Mismatch in stBLUE: %b", $time, state);
    else
        $display("<%0t> State: %b, Next: %b", $time, state, state_next);
    to_next_state;


    if(state[stWHITE] != 1'b1)
        $display("<%0t> Mismatch in stWHITE: %b", $time, state);
    else
        $display("<%0t> State: %b, Next: %b", $time, state, state_next);
    to_next_state;


    if(state[stBLACK] != 1'b1)
        $display("<%0t> Mismatch in stBLACK: %b", $time, state);
    else
        $display("<%0t> State: %b, Next: %b", $time, state, state_next);
    to_next_state;


    if(state[stIDLE] != 1'b1)
        $display("<%0t> Mismatch in stIDLE: %b", $time, state);
    else
        $display("<%0t> State: %b, Next: %b", $time, state, state_next);
    to_next_state;


    repeat(5) @(posedge clock);
    $finish();
end

task to_next_state;
begin
    @(posedge clock) #5 next  = 1'b1;
    @(posedge clock) #5 next  = 1'b0;
end
endtask // to_next_state

task reset_chip;
begin
    reset = 1'b1;
    repeat(5) @(posedge clock);
    #5 reset = 1'b0;
end
endtask

example_fsm fsm(
    .clock      (clock),     //I
    .reset      (reset),     //I
    .next       (next),      //I
    .state      (state),     //O [7:0]
    .state_next (state_next) //O [7:0]
);

endmodule
