import sys

# Declaration of global variables
INPUT_FILE = ''

# exFAT Volume Boot Record offset list
OEM_descriptor                      = [0x03, 8] #EXFAT___
partition_sector_absolute_offset    = [0x40, 8]
total_sectors_on_volume             = [0x48, 8]
location_of_fat                     = [0x50, 4] #sectors
physical_size_of_fat                = [0x54, 4] #in sectors
cluster_heap                        = [0x58, 4] #data area    / VBR + VBR copy + FAT#1 + FAT#x
number_of_clusters                  = [0x5c, 4]
root_directory                      = [0x60, 4] #Root Directory first cluster
volume_serial_number                = [0x64, 4]
active_fat                          = [0x6b, 1]
bytes_per_sector                    = [0x6c, 1] #power of 2
sectors_per_cluster                 = [0x6d, 1] #power of 2    
number_of_fats                      = [0x6e, 1] #usually 1
percentage_in_use                   = [0x70, 1]

#init of exFAT Volume Boot Record values list
PARTITION_SECTOR_OFFSET = 0
SECTOR_COUNT            = 0
FAT_LOCATION            = 0
FAT_SIZE                = 0
CLUSTER_HEAP            = 0
CLUSTER_COUNT           = 0
ROOT_DIRECTORY          = 0
VOLUME_SERIAL           = 0
ACTIVE_FAT              = 0
SECTOR_SIZE             = 0
CLUSTER_SIZE            = 0
FAT_COUNT               = 0
USE_PERCENTS            = 0

BITMAP_OFFSET           = 0
ROOT_DIRECTORY_OFFSET   = 0

def print_hex(data, _print = True):
    #print(data)
    hex = data.hex().upper()
    hex_spaces = " ".join([hex[i:i+2] for i in range(0, len(hex), 2)])
    hex_lines = "\n".join([hex_spaces[i : i+(16*3)] for i in range(0, len(hex_spaces), 16*3)])
    if _print:
        print(hex_lines)
    return hex_lines

def get_bytes(file, offset, length):
    file.seek(offset)
    return file.read(length)

def get_VBR(file):
    # tell function to use globaly declared variables
    global PARTITION_SECTOR_OFFSET
    global SECTOR_COUNT
    global FAT_LOCATION
    global FAT_SIZE
    global CLUSTER_HEAP
    global CLUSTER_COUNT
    global ROOT_DIRECTORY
    global VOLUME_SERIAL
    global ACTIVE_FAT
    global SECTOR_SIZE
    global CLUSTER_SIZE
    global FAT_COUNT
    global USE_PERCENTS
    global BITMAP_OFFSET
    global ROOT_DIRECTORY_OFFSET
    
    # 2** means power of 2
    PARTITION_SECTOR_OFFSET = int.from_bytes    (get_bytes(file,    partition_sector_absolute_offset[0],    partition_sector_absolute_offset[1]),   byteorder='little')
    SECTOR_COUNT            = int.from_bytes    (get_bytes(file,    total_sectors_on_volume[0],             total_sectors_on_volume[1]),            byteorder='little')
    FAT_LOCATION            = int.from_bytes    (get_bytes(file,    location_of_fat[0],                     location_of_fat[1]),                    byteorder='little')
    FAT_SIZE                = int.from_bytes    (get_bytes(file,    physical_size_of_fat[0],                physical_size_of_fat[1]),               byteorder='little')
    CLUSTER_HEAP            = int.from_bytes    (get_bytes(file,    cluster_heap[0],                        cluster_heap[1]),                       byteorder='little')
    CLUSTER_COUNT           = int.from_bytes    (get_bytes(file,    number_of_clusters[0],                  number_of_clusters[1]),                 byteorder='little')
    ROOT_DIRECTORY          = int.from_bytes    (get_bytes(file,    root_directory[0],                      root_directory[1]),                     byteorder='little')
    VOLUME_SERIAL           = int.from_bytes    (get_bytes(file,    volume_serial_number[0],                volume_serial_number[1]),               byteorder='little')
    ACTIVE_FAT              = int.from_bytes    (get_bytes(file,    active_fat[0],                          active_fat[1]),                         byteorder='little')
    SECTOR_SIZE             = 2**int.from_bytes (get_bytes(file,    bytes_per_sector[0],                    bytes_per_sector[1]),                   byteorder='little')
    CLUSTER_SIZE            = 2**int.from_bytes (get_bytes(file,    sectors_per_cluster[0],                 sectors_per_cluster[1]),                byteorder='little')
    FAT_COUNT               = int.from_bytes    (get_bytes(file,    number_of_fats[0],                      number_of_fats[1]),                     byteorder='little')
    USE_PERCENTS            = int.from_bytes    (get_bytes(file,    percentage_in_use[0],                   percentage_in_use[1]),                  byteorder='little')
    BITMAP_OFFSET           = CLUSTER_HEAP * SECTOR_SIZE
    ROOT_DIRECTORY_OFFSET   = (CLUSTER_HEAP + ROOT_DIRECTORY * CLUSTER_SIZE) * SECTOR_SIZE

def print_VBR():
    print("\nVBR values: \n")
    print("Partition Sector Absolute Offset: ", PARTITION_SECTOR_OFFSET)
    print("Total sectors on volume:          ", SECTOR_COUNT, " sectors")
    print("Location of FAT:                  ", FAT_LOCATION, " sectors")
    print("Physical size of FAT:             ", FAT_SIZE, " sectors")
    print("cluster heap – « data area »:     ", CLUSTER_HEAP, " sectors")
    print("Number of Clusters:               ", CLUSTER_COUNT, " clusters")
    print("Root Directory first cluster:     ", ROOT_DIRECTORY, "th cluster")
    print("Volume serial number:             ", VOLUME_SERIAL)
    print("Active FAT:                       ", ACTIVE_FAT)
    print("Sector size:                      ", SECTOR_SIZE, " bytes")
    print("Cluster size:                     ", CLUSTER_SIZE, " sectors")
    print("Number of FATs (usually 1):       ", FAT_COUNT)
    print("Percentage in use:                ", USE_PERCENTS, " %")
    print("\n") #empty line
    print("Bitmap offset:                    ", BITMAP_OFFSET, " byte")
    print("Root directory offset:            ", ROOT_DIRECTORY_OFFSET, "byte")
    print("\n") #empty line

def bitmap_position(file):      #327839 & 327832 in t.dd
    offset          = int(input("enter byte position in bitmap: "))
    relative_offset = offset - BITMAP_OFFSET
    pos_from        = relative_offset * CLUSTER_SIZE + 2 #2 because 1 is VBR cluster
    pos_to          = pos_from + 7
    pos_byte        = get_bytes(file, offset, 1)
    
    print("Relative offset: ", relative_offset)
    hex = print_hex(pos_byte)
    print("from: ", pos_from)
    print("To: ", pos_to)
    
    bit = ord(pos_byte)
    bit = bin(bit)[2:].rjust(8, '0')
    print("Allocation Status 0x", hex, " -> ", bit)
    
    for b in range(len(bit)):
        availability = 'available'
        if bit[7-b] == '1':
            availability = 'allocated'
        print(bit[7-b], ': ', pos_from+b, ' - ' + availability)

def carve_data(file):
    start           = int(input("enter start cluster: "))   #1222 in t.dd
    end             = int(input("enter end cluster: "))     #1275 in t.dd
    out_file        = input("enter output file name: ")     #will be jpg in t.dd
    clusters        = end - start + 1
    sectors         = clusters * CLUSTER_SIZE
    heap            = CLUSTER_HEAP
    sectors_to_skip = (start-2) * CLUSTER_SIZE
    print("dd if=" +INPUT_FILE+ " of=" +out_file+ " bs=" +str(SECTOR_SIZE)+ " skip=$((" +str(heap)+ "+" +str(sectors_to_skip)+ ")) count=" +str(sectors))
    
    #return  #Test zone below
    
    with open(out_file, "wb") as output:
        offset = (heap + sectors_to_skip) * SECTOR_SIZE
        print("offset",offset)
        file.seek(offset)                   # <- need offset byte
        for i in range(sectors):
            data = file.read(SECTOR_SIZE)
            output.write(data)

# Programs entry function
def Main():
    global INPUT_FILE
    INPUT_FILE = input('Input file: ')
    
    with open(INPUT_FILE, "rb") as file_in:
        get_VBR(file_in)
        print_VBR()
        command = ""
        
        #### GIVE INSTRUCTIONS ####
        while True:
            command = str(input("Give instructions: "))
            
            if command == "exit":
                break
            
            elif command == "print vbr":
                print_VBR()
            
            elif command == "bitmap position":
                bitmap_position(file_in)
            
            elif command == "carve data":
                carve_data(file_in)
            
            elif command == "help":
                print("print vbr       - prints all VBR properties.")
                print("bitmap position - give position byte for gathering cluster allocation status.")
                print("carve data      - give start and end cluster to export bytes into separate file.")
                print("exit            - will exit the script. \n")
            
            else:
                print("Command does not exists: ", command)

# Declare entry function
if __name__ == '__main__':                  #triggered by call from terminal
    Main()

