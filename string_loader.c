#include <fileioc.h>

char* get_string_pointer(const char file_name[9], const uint8_t index, const uint8_t header_string_length) {
    // In: file_name : null terminated string of the AppVar name
    // index: index of the string to get
    // header_string_length: Length of the header string, including possible \0 ending
    // Return: Pointer of the string if success, NULL if not
    char* pointer = NULL;
    uint8_t var;
    var = ti_Open(file_name, "r");
    if (var == 0) {  // Opening file failed
        return pointer;
    }
    ti_Seek(header_string_length, SEEK_SET, var);  // Skip header string
    int24_t tmp_num = ti_GetC(var);  // Note: ti_GetC seeks to the next char
    if (tmp_num == EOF) {
        return pointer;
    }
    uint8_t header_size = (uint8_t)tmp_num;  // header size is uint8_t, however we needed to check if it's not EOF(-1)
    int24_t counter = 0;
    for (uint8_t index_l = 0; index_l < index; index_l++) {
        tmp_num = ti_GetC(var);
        if (tmp_num == EOF) {
            return pointer;
        }
        counter += (uint8_t)tmp_num;  // Adding all previous strings' length to get the string location
    }  // The file has an header (containing its size and then the size of strings (both max 255) and then \0 separated strings.
    ti_Seek(header_string_length + header_size + counter, SEEK_SET, var);  // Seek to the desired string location
    pointer = ti_GetDataPtr(var);  // Getting the pointer at this location
    ti_Close(var);
    return pointer;
}