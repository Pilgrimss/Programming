#include <stdio.h>
#include <stdlib.h>
#include <time.h>

#include <sys/time.h>

#include "memory_access.h"
#include "register_access.h"
#include "ALU.h"
#include "io.h"
#include "execution.h"


//C implementation of my CPU 10

int step(unsigned int *registers, unsigned char *MEMORY){   //returns halt, carries out game logic
	unsigned int instruction = 0;
	unsigned int address = 0;
	unsigned char decoded[4];

	unsigned char instr;
	unsigned char reg1;
	unsigned char reg2;
	unsigned char conditional;

	instruction = fetch_instruction(registers,MEMORY);
	address = fetch_address(registers,MEMORY);

	debug_instruction(decoded,instruction);

	//int i;
	//for (i = 0; i<4;i++){
	//	printf("%i   ", (int) decoded[i]);
	//}
	//printf("\n");
	
	instr = decoded[0];
	reg1 = decoded[1]&15;
	reg2 = decoded[2]&15;
	conditional = decoded[3];
	return execute(instr,reg1,reg2,conditional,address,registers,MEMORY);   //returned value is 1 if needs to return, otherwise false

}

int debug_step(unsigned int *registers, unsigned char *MEMORY){   //returns halt, carries out game logic
	unsigned int instruction = 0;
	unsigned int address = 0;
	unsigned char decoded[4];

	unsigned char instr;
	unsigned char reg1;
	unsigned char reg2;
	unsigned char conditional;

	instruction = fetch_instruction(registers,MEMORY);
	address = fetch_address(registers,MEMORY);

	debug_instruction(decoded,instruction);






	
	instr = decoded[0];
	reg1 = decoded[1]&15;
	reg2 = decoded[2]&15;
	conditional = decoded[3];

	printf("\n%u|  ",registers[4] - 8);

	printf("%i   ", (int) instr);
	printf("%i   ", (int) reg1);
	printf("%i   ", (int) reg2);
	printf("%i   ", (int) conditional);

	printf(" address = %u\n", address);
	getchar();

	return execute(instr,reg1,reg2,conditional,address,registers,MEMORY);   //returned value is 1 if needs to return, otherwise false

}

void init_memory(unsigned char *MEMORY, char *name){
	char state;   //uses a state machine to switch between address and data
	unsigned int address;
	unsigned char chr; 	//exctracted character
	int i = 0;
	FILE *fp = fopen(name, "rb");  //get file
	if (fp == NULL){ 				//check valid file
		printf("ERROR: Failed to open file \"%s\"\n",name);
		exit(1);
	}
	//file in format addr,addr,addr,addr,data,stop?
	state = 0;
	while (state != 6){   //parsing state machine, state of 6 ==> halt;
		fread(&chr,1,1,fp);
		//getchar();

		if (state == 0){
			//printf("%x\n",chr);
			state = 1;
			address = chr;
		}
		else if (state == 1){
			//printf("%x\n",chr);
			state = 2;
			address = address << 8;
			address = address + chr;
		}
		else if (state == 2){
			//printf("%x\n",chr);
			state = 3;
			address = address << 8;
			address = address + chr;
		}
		else if (state == 3){
			//printf("%x\n",chr);
			state = 4;
			address = address << 8;
			address = address + chr;

			//printf("address = %u\n",address );
		}
		else if (state == 4){
			//printf("chr = %x\n",chr );
			state = 5;
			store_byte_memory(address,chr,MEMORY);
		}
		else if (state == 5){ //sixth byte is 1 for an EOF or 0 for continue
			//printf("hit state 5: %x\n",chr);
			if (chr == 1){
				state = 6;
			}
			else if (chr == 0){
				state = 0;
			}
			else{
				exit(1);
			}
		}
	}
	fclose(fp);
}

void alt_init_memory(unsigned char *MEMORY, char *name){
	FILE *fp = fopen(name, "rb");
	if (fp == NULL){
		printf("ERROR: Failed to open file \"%s\"\n",name);
		exit(1);
	}
}

int main(int argc, char *argv[]){
	static unsigned char MEMORY[1048576] = {0}; 					//setting up memory and registers
	static unsigned int registers[16] = {0,1};
	int halt = 0;
	long count = 0;

	//______ Timing variables _____
	struct timeval begin;
	struct timeval end;
	long seconds_elapsed;
	long useconds_elapsed;
	double time_elapsed;
	double instructions_per_second;

	printf("initialising memory\n");
	init_memory(MEMORY,argv[1]);
	
	if (argc < 3){

		printf("______________________ running ______________________\n");
		gettimeofday(&begin,NULL);
		while (halt == 0){
			count += 1;
			halt = step(registers,MEMORY);
		}
		gettimeofday(&end,NULL);

		seconds_elapsed = (end.tv_sec - begin.tv_sec); //(double) (end.tv_usec - begin.tv_usec)/1000000 + 
		useconds_elapsed = end.tv_usec - begin.tv_usec;
		time_elapsed = (double)seconds_elapsed + ((double)useconds_elapsed)/1000000;
		instructions_per_second = count/time_elapsed; 
		printf("\n______________________ Execution halted ______________________\n");
		printf("executed %u instructions in ",count);
		printf("%lf seconds ", time_elapsed);
		if (time_elapsed > 0.0001){
			printf("at %lf ips\n", instructions_per_second);
		}
	} else {
		if (argc == 3){	

			printf("______________________ running Debug ______________________\n");
			gettimeofday(&begin,NULL);
			while (halt == 0){
				count += 1;
				halt = debug_step(registers,MEMORY);
			}
			gettimeofday(&end,NULL);	

			seconds_elapsed = (end.tv_sec - begin.tv_sec); //(double) (end.tv_usec - begin.tv_usec)/1000000 + 
			useconds_elapsed = end.tv_usec - begin.tv_usec;
			time_elapsed = (double)seconds_elapsed + ((double)useconds_elapsed)/1000000;
			instructions_per_second = count/time_elapsed; 
			printf("\n______________________ Execution halted ______________________\n");
			printf("executed %u instructions in ",count);
			printf("%lf seconds ", time_elapsed);
			if (time_elapsed > 0.0001){
				printf("at %lf ips\n", instructions_per_second);
				}
		} else {
			int debug_threshold = atoi(argv[3]);

			printf("______________________ running Debug ______________________\n");
			gettimeofday(&begin,NULL);
			while (halt == 0 && count < debug_threshold){
				count += 1;
				halt = step(registers,MEMORY);
			}
			while (halt == 0){
				count += 1;
				halt = debug_step(registers,MEMORY);
			}
			gettimeofday(&end,NULL);	

			seconds_elapsed = (end.tv_sec - begin.tv_sec); //(double) (end.tv_usec - begin.tv_usec)/1000000 + 
			useconds_elapsed = end.tv_usec - begin.tv_usec;
			time_elapsed = (double)seconds_elapsed + ((double)useconds_elapsed)/1000000;
			instructions_per_second = count/time_elapsed; 
			printf("\n______________________ Execution halted ______________________\n");
			printf("executed %u instructions in ",count);
			printf("%lf seconds ", time_elapsed);
			if (time_elapsed > 0.0001){
				printf("at %lf ips\n", instructions_per_second);
				}
		}
	}
	return 0;
}






