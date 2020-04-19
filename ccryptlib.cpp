

extern "C" int* encrypt(const char* plaintext, long int size, const char* key) {
    
    int keyLen(0);
    while (key[keyLen]!='\0') keyLen++;
    
    int* crypted = new int[size];
    int* byteKey = new int[keyLen];
    for (int i=0; i<keyLen; i++) {
        byteKey[i] = key[i];
    }
    for (int i=0; i<size; i++) {
        crypted[i] = (plaintext[i] + byteKey[i%keyLen] + 256)%256;
    }
    return crypted;
}

extern "C" int* decrypt(const char* crypted, long int size, const char* key) {
    
    int keyLen(0);
    while (key[keyLen]!='\0') keyLen++;
    
    int* plaintext = new int[size];
    int* byteKey = new int[keyLen];
    for (int i=0; i<keyLen; i++) {
        byteKey[i] = 256-key[i];
    }
    for (int i=0; i<size; i++) {
        plaintext[i] = (crypted[i] + byteKey[i%keyLen] + 256)%256;
    }
    return plaintext;
}

// the argument long int size because to test the speed, the empty file
// is filled with '\0' (python file.truncate)


//g++ -c -fPIC ccryptlib.cpp -o ccryptlib.o -O3
//g++ -shared -Wl,-soname,library.so -o ccryptlib.so ccryptlib.o -O3












