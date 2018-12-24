all:  rgb_led_run png

png: rgb_led.dot
	dot -Tpng rgb_led.dot -o rgb_led.png

rgb_led.v: rgb_led.dot
	../../tizzy.py -o rgb_led.v rgb_led.dot


rgb_led_sim: rgb_led.v
	iverilog -o rgb_led_sim tb_rgb_led.v rgb_led.v


rgb_led_run: rgb_led_sim
	./rgb_led_sim

.PHONY: clean
clean:
	rm -f rgb_led.png rgb_led.v rgb_led.vh rgb_led_sim

