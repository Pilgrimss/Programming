--------------------------------------------------------------------------------
-- Copyright (c) 1995-2003 Xilinx, Inc.
-- All Right Reserved.
--------------------------------------------------------------------------------
--   ____  ____ 
--  /   /\/   / 
-- /___/  \  /    Vendor: Xilinx 
-- \   \   \/     Version : 10.1.03
--  \   \         Application : ISE
--  /   /         Filename : PCI_Config.vhw
-- /___/   /\     Timestamp : Thu Mar 12 18:22:02 2009
-- \   \  /  \ 
--  \___\/\___\ 
--
--Command: 
--Design Name: PCI_Config
--Device: Xilinx
--

library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
USE IEEE.STD_LOGIC_TEXTIO.ALL;
USE IEEE.STD_LOGIC_ARITH.ALL;
USE IEEE.STD_LOGIC_UNSIGNED.ALL;
USE STD.TEXTIO.ALL;

ENTITY PCI_Config IS
END PCI_Config;

ARCHITECTURE testbench_arch OF PCI_Config IS
    FILE RESULTS: TEXT OPEN WRITE_MODE IS "results.txt";

    COMPONENT DC7_PCI
        PORT (
            PCI_Clock : In std_logic;
            PCI_Reset : In std_logic;
            IRdy : In std_logic;
            Frame : In std_logic;
            IDSel : In std_logic;
            TRdy : Out std_logic;
            DevSel : Out std_logic;
            CBE : In std_logic_vector (3 DownTo 0);
            AD : InOut std_logic_vector (17 DownTo 0);
            ADEx : In std_logic_vector (1 DownTo 0);
            USBRxValid : In std_logic;
            USBTxReady : In std_logic;
            USBData : InOut std_logic_vector (7 DownTo 0);
            USBRead : Out std_logic;
            USBWrite : Out std_logic;
            DData : InOut std_logic;
            DClock : Out std_logic;
            SSClock : Out std_logic;
            SSAddr : Out std_logic;
            SSStrobe : Out std_logic;
            SSDOut : Out std_logic;
            SSDIn : In std_logic;
            SSAck : In std_logic;
            LED : Out std_logic;
            Probe : Out std_logic
        );
    END COMPONENT;

    SIGNAL PCI_Clock : std_logic := '0';
    SIGNAL PCI_Reset : std_logic := '0';
    SIGNAL IRdy : std_logic := '0';
    SIGNAL Frame : std_logic := '0';
    SIGNAL IDSel : std_logic := '0';
    SIGNAL TRdy : std_logic := '0';
    SIGNAL DevSel : std_logic := '0';
    SIGNAL CBE : std_logic_vector (3 DownTo 0) := "0000";
    SIGNAL AD : std_logic_vector (17 DownTo 0) := "000000000000000000";
    SIGNAL ADEx : std_logic_vector (1 DownTo 0) := "00";
    SIGNAL USBRxValid : std_logic := '0';
    SIGNAL USBTxReady : std_logic := '0';
    SIGNAL USBData : std_logic_vector (7 DownTo 0) := "00000000";
    SIGNAL USBRead : std_logic := '0';
    SIGNAL USBWrite : std_logic := '0';
    SIGNAL DData : std_logic := '0';
    SIGNAL DClock : std_logic := '0';
    SIGNAL SSClock : std_logic := '0';
    SIGNAL SSAddr : std_logic := '0';
    SIGNAL SSStrobe : std_logic := '0';
    SIGNAL SSDOut : std_logic := '0';
    SIGNAL SSDIn : std_logic := '0';
    SIGNAL SSAck : std_logic := '0';
    SIGNAL LED : std_logic := '0';
    SIGNAL Probe : std_logic := '0';

    constant PERIOD : time := 30 ns;
    constant DUTY_CYCLE : real := 0.5;
    constant OFFSET : time := 15 ns;
shared    variable TimeNow : time:= 0 ns;
    
    BEGIN
        UUT : DC7_PCI
        PORT MAP (
            PCI_Clock => PCI_Clock,
            PCI_Reset => PCI_Reset,
            IRdy => IRdy,
            Frame => Frame,
            IDSel => IDSel,
            TRdy => TRdy,
            DevSel => DevSel,
            CBE => CBE,
            AD => AD,
            ADEx => ADEx,
            USBRxValid => USBRxValid,
            USBTxReady => USBTxReady,
            USBData => USBData,
            USBRead => USBRead,
            USBWrite => USBWrite,
            DData => DData,
            DClock => DClock,
            SSClock => SSClock,
            SSAddr => SSAddr,
            SSStrobe => SSStrobe,
            SSDOut => SSDOut,
            SSDIn => SSDIn,
            SSAck => SSAck,
            LED => LED,
            Probe => Probe
        );

        PROCESS    -- clock process for PCI_Clock
        BEGIN
            WAIT for OFFSET;
            CLOCK_LOOP : LOOP
                PCI_Clock <= '0';
		TimeNow := TimeNow +(PERIOD - (PERIOD * DUTY_CYCLE));
                WAIT FOR (PERIOD - (PERIOD * DUTY_CYCLE));
                PCI_Clock <= '1';
		TimeNow := TimeNow +(PERIOD * DUTY_CYCLE);
                WAIT FOR (PERIOD * DUTY_CYCLE);
            END LOOP CLOCK_LOOP;
        END PROCESS;


		
		



        PROCESS
            BEGIN
	    
                WAIT FOR 73 ns;

		--	===========================	Initial conditions and reset	=============================================
                -- -------------  Current Time:  73ns
                AD <= "ZZZZZZZZZZZZZZZZZZ";
                DData <= '1';
                Frame <= '1';
                IRdy <= '1';
                USBRxValid <= '1';
                USBTxReady <= '1';
		SSAck <= '1';
		
                WAIT FOR 60 ns;
                -- -------------  Current Time:  
                PCI_Reset <= '1';
                WAIT FOR 30 ns;
		
		
		--	==================================	CONFIG READ CYCLE	==========================

               -- -------------  Current Time:  
                CBE <= "1010";	--	ConfigRead
                WAIT FOR 30 ns;

                -- -------------  Current Time:  
                Frame <= '0';
                IDSel <= '1';					-- select the board
                AD <= "000001000000000000";	-- address = $1000
                WAIT FOR 30 ns;

                -- -------------  Current Time:  
                IDSel <= '0';
                IRdy <= '0';
                AD <= "ZZZZZZZZZZZZZZZZZZ";
                WAIT FOR 60 ns;

                -- -------------  Current Time:  
                Frame <= '1';
                WAIT FOR 30 ns;

                -- -------------  Current Time:  
                IRdy <= '1';
                WAIT FOR 60 ns;
		
		--	==========================================	PCI Read from Port $0318	==================================================
              
                -- -------------  Current Time:  
                CBE <= "0010";
                WAIT FOR 30 ns;

                -- -------------  Current Time:  
                Frame <= '0';
                AD <= "000000001100011000";
                WAIT FOR 30 ns;

                -- -------------  Current Time:  
                IRdy <= '0';
                AD <= "ZZZZZZZZZZZZZZZZZZ";
                CBE <= "0011";
                WAIT FOR 30 ns;

                -- -------------  Current Time:  
                Frame <= '1';
                WAIT FOR 30 ns;

                -- -------------  Current Time:  
                IRdy <= '1';
                WAIT FOR 60 ns;
		
		
		--	====================================	PCI Write Byte $3A to Port $0318 (SSI Address)	======================================================
		
                -- (CBE is already 0011)
                -- -------------  Current Time:  
                Frame <= '0';
                AD <= "000000001100011000";
                CBE <= "0011";
                WAIT FOR 30 ns;

                -- -------------  Current Time:  
                IRdy <= '0';
                AD <= "000000000000111010";
                CBE <= "0001";
                WAIT FOR 60 ns;

                -- -------------  Current Time:  
                Frame <= '1';
                WAIT FOR 30 ns;

                -- -------------  Current Time:  
                IRdy <= '1';

		
                WAIT FOR 120 ns;



		--	====================================	PCI Write Word $07C59 to Port $318 (SSI Data)	======================================================

                -- -------------  Current Time: 795ns 
                Frame <= '0';
                AD <= "000000001100011000";
                CBE <= "0011";
                WAIT FOR 30 ns;

                -- -------------  Current Time:  
                IRdy <= '0';
                AD <= "000111110001011001";
                WAIT FOR 60 ns;

                -- -------------  Current Time:  
                Frame <= '1';
                SSAck <= '0';
                WAIT FOR 30 ns;

                -- -------------  Current Time:  
                IRdy <= '1';
                SSAck <= '1';
                WAIT FOR 510 ns;

                -- -------------  Current Time:  
                SSAck <= '0';
                WAIT FOR 30 ns;

                -- -------------  Current Time:  
                SSAck <= '1';
                WAIT FOR 100 ns;	--	wait for SSI transaction to complete

		--	=================================	USB Read	===========================================================

                -- -------------  Current Time:  
                USBRxValid <= '0';
		USBData		<= x"45";
                WAIT FOR 100 ns;


                -- -------------  Current Time:  
                CBE <= "0010";
                WAIT FOR 30 ns;

                -- -------------  Current Time:  
                Frame <= '0';
                AD <= "000000001100011010";	--	Port address $031A
                WAIT FOR 30 ns;

                -- -------------  Current Time:  
                IRdy <= '0';
                AD <= "ZZZZZZZZZZZZZZZZZZ";
                CBE <= "0011";
                WAIT FOR 30 ns;

                -- -------------  Current Time:  
                Frame <= '1';
                WAIT FOR 150 ns;

                -- -------------  Current Time:  
                IRdy <= '1';
                WAIT FOR 120 ns;
		
		USBTxReady	<= '0';
		USBData		<= "ZZZZZZZZ";
                WAIT FOR 120 ns;
		
		--	====================================	PCI Write Byte $3A to Port $031A (USB Address)	======================================================

                -- -------------  Current Time:  
                Frame <= '0';
                AD <= "000000001100011010";
                CBE <= "0011";
                WAIT FOR 30 ns;

                -- -------------  Current Time:  
                IRdy <= '0';
                AD <= "000000000000111010";
                CBE <= "0001";
                WAIT FOR 60 ns;

                -- -------------  Current Time:  
                Frame <= '1';
                WAIT FOR 30 ns;

                -- -------------  Current Time:  
                IRdy <= '1';

		
                WAIT FOR 120 ns;



		

                WAIT FOR 1560 ns;


		--	============================================================================================================


                -- -------------  Current Time:  
                SSAck <= '0';

                WAIT FOR 30 ns;
                -- -------------  Current Time:  
                SSAck <= '1';

                -- -------------------------------------
                WAIT FOR 97227 ns;
                -- -------------  Current Time:  

            END PROCESS;

    END testbench_arch;

