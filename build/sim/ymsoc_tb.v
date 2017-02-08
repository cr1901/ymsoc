`timescale 1ns/1ps

module ymsoc_tb();
reg sys_rst;
reg sys_clk;

wire ct1, ct2;
wire audio_l, audio_r;
wire led1, led2, led3, led4, led5, led6;


// clock
initial sys_clk = 1'b0;
always #15.625 sys_clk = ~sys_clk;

// reset
initial begin
	sys_rst = 1'b1;
	#20
	sys_rst = 1'b0;
end


top dut(
    .clk32(sys_clk),
    .user_led(ct1),
    .user_led_1(ct2),
	.audio_a0(audio_l),
	.audio_a1(audio_r)
/*    .user_led_2(led1),
    .user_led_3(led2),
    .user_led_4(led3),
    .user_led_5(led4),
    .user_led_6(led5),
    .user_led_7(led6) */
);


initial begin
    $dumpfile("ymsoc.vcd");
    $dumpvars(0, dut);
	$dumpoff;
	#6000000;
	$dumpon;
end


always @ (posedge sys_clk)
begin
    if($time > 12000000) begin
        $finish;
    end
end

endmodule
