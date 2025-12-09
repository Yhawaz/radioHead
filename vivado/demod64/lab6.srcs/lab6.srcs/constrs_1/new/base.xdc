## USER LEDS
set_property PACKAGE_PIN AR11 [ get_ports "led[0]" ]
set_property IOSTANDARD LVCMOS18 [ get_ports "led[0]" ]

set_property PACKAGE_PIN AW10 [ get_ports "led[1]" ]
set_property IOSTANDARD LVCMOS18 [ get_ports "led[1]" ]

set_property PACKAGE_PIN AT11 [ get_ports "led[2]" ]
set_property IOSTANDARD LVCMOS18 [ get_ports "led[2]" ]

set_property PACKAGE_PIN AU10 [ get_ports "led[3]" ]
set_property IOSTANDARD LVCMOS18 [ get_ports "led[3]" ]

## USER SLIDE SWITCH
set_property PACKAGE_PIN AN13 [ get_ports "sw[0]" ]
set_property IOSTANDARD LVCMOS18 [ get_ports "sw[0]" ]

set_property PACKAGE_PIN AU12 [ get_ports "sw[1]" ]
set_property IOSTANDARD LVCMOS18 [ get_ports "sw[1]" ]

set_property PACKAGE_PIN AW11 [ get_ports "sw[2]" ]
set_property IOSTANDARD LVCMOS18 [ get_ports "sw[2]" ]

set_property PACKAGE_PIN AV11 [ get_ports "sw[3]" ]
set_property IOSTANDARD LVCMOS18 [ get_ports "sw[3]" ]

## PMODS

set_property PACKAGE_PIN AF16 [ get_ports "data[0]" ]
set_property PACKAGE_PIN AG17 [ get_ports "data[1]" ]
set_property PACKAGE_PIN AJ16 [ get_ports "data[2]" ]
set_property PACKAGE_PIN AK17 [ get_ports "data[3]" ]
set_property PACKAGE_PIN AF15 [ get_ports "data[4]" ]
set_property PACKAGE_PIN AF17 [ get_ports "data[5]" ]
set_property PACKAGE_PIN AH17 [ get_ports "data[6]" ]
set_property PACKAGE_PIN AK16 [ get_ports "data[7]" ]
set_property IOSTANDARD LVCMOS18 [ get_ports "data*"]

## USER PUSH BUTTON
set_property PACKAGE_PIN AV12 [ get_ports "btn" ]
set_property IOSTANDARD LVCMOS18 [ get_ports "btn" ]

#set_property PACKAGE_PIN AV10 [ get_ports "PB_1" ]
#set_property IOSTANDARD LVCMOS18 [ get_ports "PB_1" ]

#set_property PACKAGE_PIN AW9 [ get_ports "PB_2" ]
#set_property IOSTANDARD LVCMOS18 [ get_ports "PB_2" ]

#set_property PACKAGE_PIN AT12 [ get_ports "PB_3" ]
#set_property IOSTANDARD LVCMOS18 [ get_ports "PB_3" ]

#set_property PACKAGE_PIN AN12 [ get_ports "PB_4" ]
#set_property IOSTANDARD LVCMOS18 [ get_ports "PB_4" ]



set_property BITSTREAM.CONFIG.UNUSEDPIN PULLUP [current_design]
set_property BITSTREAM.CONFIG.OVERTEMPSHUTDOWN ENABLE [current_design]
set_property BITSTREAM.GENERAL.COMPRESS TRUE [current_design]