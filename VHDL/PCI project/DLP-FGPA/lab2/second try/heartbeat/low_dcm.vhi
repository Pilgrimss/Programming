
-- VHDL Instantiation Created from source file low_dcm.vhd -- 16:27:47 12/15/2012
--
-- Notes: 
-- 1) This instantiation template has been automatically generated using types
-- std_logic and std_logic_vector for the ports of the instantiated module
-- 2) To use this template to instantiate this entity, cut-and-paste and then edit

	COMPONENT low_dcm
	PORT(
		CLKIN_IN : IN std_logic;
		RST_IN : IN std_logic;          
		CLKDV_OUT : OUT std_logic;
		CLKIN_IBUFG_OUT : OUT std_logic;
		CLK0_OUT : OUT std_logic;
		LOCKED_OUT : OUT std_logic
		);
	END COMPONENT;

	Inst_low_dcm: low_dcm PORT MAP(
		CLKIN_IN => ,
		RST_IN => ,
		CLKDV_OUT => ,
		CLKIN_IBUFG_OUT => ,
		CLK0_OUT => ,
		LOCKED_OUT => 
	);


