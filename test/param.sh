gcc -ffunction-sections --param ssp-buffer-size=4 -fdata-sections -g -ftree-ter -c 1.c -o param-1.o
gcc -faggressive-loop-optimizations  --param ssp-buffer-size=8 -falign-functions=1 --param ipcp-unit-growth=100 -fdata-sections -g -c fs.c -o param-2.o
gcc param-{1,2}.o -o param
../flagsup.py --full param
