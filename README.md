# PyCrypt
An program to encrypt / decrypt files and directories

## How it works
### File encryption
Read a file as binary, encrypt it with a key (the password entered) and then write a file with the encrypted file and the key.

### Folder encryption
Build an index with every files of the folder crypted and the empty directories. Put them with the key in a file.  
For decryption, the folder will be rebuilt according to the index by decrypting each enrty.  

## Is it secure ?
__No__. The key (password) is hashed with SHA256 so it can take some time to find if it is long and complex.  

## External C++ library
The `ccryptlib.cpp` file contains the functions to encrypt and decrypt an array of bytes.  
It can be compiled with: __`g++ -c -fPIC ccryptlib.cpp -o ccryptlib.o -O3`__  
and then: __`g++ -shared -Wl,-soname,library.so -o ccryptlib.so ccryptlib.o -O3`__  
If the `ccryptlib.so` library is not found, the encryption will be done by the python version  
The `ccryptlib.so` in the repository is compiled with __`g++ (Ubuntu 7.5.0-3ubuntu1~18.04) 7.5.0`__.

## Updates

### 19/04/2020
 - Use external C++ library to speed up encryption.  

### 18/04/2020
 - Disable radiobutton and the pw entry
 - Replace password by stars and show only the letter on the left of the cursor
