#include <conio.h>

void out_char(unsigned int data){
	unsigned char output;
	output = data &255;
	printf("%c",output );
}

void out_data(unsigned int data){
	printf("%u\n", data);

}

unsigned int input(){
	unsigned int input_data;
	if (kbhit()!=0){
		input_data = (unsigned int)getchar();
	}
	else{
		input_data = 0;
	}
	return input_data;
}