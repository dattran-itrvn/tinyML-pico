#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define ARG_COUNT          2
#define ARG_EXE            0
#define ARG_FILENAME       1

#define FALSE              0
#define TRUE               1
#define BUFF_SIZE          256


int main(int argc, char* argv[])
{
   FILE* FileR = NULL;
   FILE* FileW = NULL;
   long FileSize = 0;
   unsigned char Count;
   unsigned char Len;
   unsigned char Value;
   unsigned char StartFlag;
   unsigned char StartFlagHeader;
   unsigned char* Pos = NULL;
   unsigned char* FileData = NULL;
   unsigned char* FileData1 = NULL;
   unsigned char Buffer[BUFF_SIZE+1];
   unsigned char BufferHeader[BUFF_SIZE+1];


   if (argc != ARG_COUNT)
	   printf("\r\n%s [HEXDUMP_FILE]\r\n\r\n", argv[ARG_EXE]);
   else
   {
      /**********************************************/
      /* Open audio hex dump text file for reading. */
      /**********************************************/
      if (!(FileR = fopen(argv[ARG_FILENAME], "rb")))
    	  printf("Failed to open file for reading: %s\r\n", argv[ARG_FILENAME]);
      else
      {
      /******************/
      /* Get file size. */
      /******************/
        fseek(FileR, 0, SEEK_END);
        FileSize = ftell(FileR);
        fseek(FileR, 0, SEEK_SET);
      /*******************************/
      /* Fead file data into memory. */
      /*******************************/
        if ((FileData = (unsigned char*)malloc(FileSize)))
        	fread(FileData, FileSize, 1, FileR);
        fclose(FileR);

      /*****************************************************/
      /* Convert file data from hex bytes to binary bytes. */
      /*****************************************************/

      // WRITE HEADER
        if (FileData){
		strcpy(Buffer, argv[ARG_FILENAME]);
		if ((Pos = strrchr(Buffer, '.')))
		   Pos[0] = '\0';
		strcat(Buffer, ".wav");
		if (!(FileW = fopen(Buffer, "wb+")))
		   printf("Failed to open file for writing: %s\r\n", Buffer);
		else{
               if ((Pos = strtok(FileData, "\n"))){
                  StartFlagHeader = FALSE;
                  do{
                     if (!strcmp(Pos, "----- END HEADER -----"))
                        break;

                     if (StartFlagHeader){
                        Len = strlen(Pos);
                        for (Count = 0; Count < Len; Count += 2){
                           Value = 0;
                           Value += (Pos[Count] >= 'A' && Pos[Count] <= 'F')?16*(10 + Pos[Count] - 'A'):16*(Pos[Count] - '0');
                           Value += (Pos[Count+1] >= 'A' && Pos[Count+1] <= 'F')?(10 + Pos[Count+1] - 'A'):(Pos[Count+1] - '0');
                           fputc(Value, FileW);

                        }
                     }

                     if (!strcmp(Pos, "----- START HEADER -----"))
                        StartFlagHeader = TRUE;

                  }
                  while ((Pos = strtok(NULL, "\n")));
               }
            }
         }
      }


      if (!(FileR = fopen(argv[ARG_FILENAME], "rb")))
    	  printf("Failed to open file for reading: %s\r\n", argv[ARG_FILENAME]);
      else{
	/******************/
	/* Get file size. */
	/******************/
	  fseek(FileR, 0, SEEK_END);
	  FileSize = ftell(FileR);
	  fseek(FileR, 0, SEEK_SET);
	/*******************************/
	/* Fead file data into memory. */
	/*******************************/
	  if ((FileData1 = (unsigned char*)malloc(FileSize)))
		  fread(FileData1, FileSize, 1, FileR);
	  fclose(FileR);

	/*****************************************************/
	/* Convert file data from hex bytes to binary bytes. */
	/*****************************************************/

	// WRITE DATA
	  if (FileData1){
		 if ((Pos = strtok(FileData1, "\n"))){
			 StartFlag = FALSE;
			 do{
				 if (!strcmp(Pos, "----- END DATA -----"))
					break;

				 if (StartFlag){
					Len = strlen(Pos);
					for (Count = 0; Count < Len; Count += 2){
					   Value = 0;
					   Value += (Pos[Count] >= 'A' && Pos[Count] <= 'F')?16*(10 + Pos[Count] - 'A'):16*(Pos[Count] - '0');
					   Value += (Pos[Count+1] >= 'A' && Pos[Count+1] <= 'F')?(10 + Pos[Count+1] - 'A'):(Pos[Count+1] - '0');
					   fputc(Value, FileW);
					   }
				 }

				 if (!strcmp(Pos, "----- START DATA -----"))
					StartFlag = TRUE;

			  }
			 while ((Pos = strtok(NULL, "\n")));
			 fclose(FileW);
		 }
	  }
      }
   }

   return 0;
}
