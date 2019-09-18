from datetime import datetime
import random
import pickle

class physical_storage_system:
    
    def __init__(self):
        
        self.size_A = 200
        self.size_B = 300
        self.total_size = self.size_A + self.size_B
        self.disk_A_data = ['0'*100]*self.size_A
        self.disk_A_metadata = [0]*self.size_A
        self.disk_B_data = ['0'*100]*self.size_B
        self.disk_B_metadata = [0]*self.size_B
    
    def iscorrect(self,block_number):
        if block_number>0 and block_number<=500:
            return True
        return False
    
    def resolve_block_number(self,block_number):
        if block_number<=200:
            return 'A',block_number-1
        else:
            return 'B',block_number-201
    
    def read_block_data(self,block_number):
        disk, block_number = self.resolve_block_number(block_number)
        print(disk, block_number)
        if disk=='A':
            return self.disk_A_data[block_number][:self.disk_A_metadata[block_number]]
        elif disk=='B':
            return self.disk_B_data[block_number][:self.disk_B_metadata[block_number]]
        
    def write_block_data(self,block_number,block_info):
        print(block_number)
        disk, block_number = self.resolve_block_number(block_number)
        print(disk,block_number)
        data_length = len(block_info)
        block_info += '0'*100
        block_info = block_info[:100]
        if disk=='A':
            self.disk_A_metadata[block_number] = data_length
            self.disk_A_data[block_number] = block_info
        elif disk=='B':
            self.disk_B_metadata[block_number] = data_length
            self.disk_B_data[block_number] = block_info

class virtual_storage_system(physical_storage_system):
    
    def __init__(self):
        super().__init__()
        self.disk_dictionary = dict()
        self.space_list = [[0,self.total_size-1,0]]
        self.space_available = self.total_size
        self.next_available_id = 11
    
    def create_disk(self,disk_size):
        if self.space_available < disk_size:
            return -1
        disk_id = 'virtual_disk_'+str(self.next_available_id)
        self.next_available_id += 1
        self.space_available -= disk_size
        self.disk_dictionary[disk_id] = []
        for i in range(len(self.space_list)):
            if not self.space_list[i][2]:
                if (self.space_list[i][1]-self.space_list[i][0]+1) < disk_size:
                    self.space_list[i][2] = 1
                    self.disk_dictionary[disk_id] += [self.space_list[i][:2]]
                    disk_size -= (self.space_list[i][1]-self.space_list[i][0]+1)
                elif (self.space_list[i][1]-self.space_list[i][0]+1) == disk_size:
                    self.space_list[i][2] = 1
                    self.disk_dictionary[disk_id] += [self.space_list[i][:2]]
                    break
                elif (self.space_list[i][1]-self.space_list[i][0]+1) > disk_size:
                    temp = self.space_list[i][1]
                    self.space_list[i][1] = self.space_list[i][0] + disk_size - 1
                    self.space_list[i][2] = 1
                    self.space_list.insert(i+1,[self.space_list[i][1]+1,temp,0])
                    self.disk_dictionary[disk_id] += [self.space_list[i][:2]]
                    break
        return disk_id
        
    def display_virtual_disks_names(self):
        print('List of all Virtual Disks :')
        for (i,j) in enumerate(list(self.disk_dictionary.keys())):
            print(str(i+1)+'. '+str(j))
            
    def resolve_disk_number(self,disk_number):
        if disk_number<=0 or disk_number>len(self.disk_dictionary):
            return -1
        return list(self.disk_dictionary.keys())[disk_number-1]
    
    def delete_disk(self,disk_id):
        
        space = 0
        for i in self.disk_dictionary[disk_id]:
            space += i[1]-i[0]+1
        self.space_available += space
        
        for i in self.disk_dictionary[disk_id]:
            for j in range(len(self.space_list)):
                if self.space_list[j][0]==i[0] and self.space_list[j][1]==i[1]:
                    self.space_list[j][2] = 0
        temp = [self.space_list[0]]
        self.space_list = self.space_list[1:]
        while self.space_list:
            if temp[-1][2]==0 and self.space_list[0][2]==0:
                temp[-1][1] = self.space_list[0][1]
            else:
                temp.append(self.space_list[0])
            self.space_list = self.space_list[1:]
        self.space_list = temp
        
        del self.disk_dictionary[disk_id]
        return disk_id
        
    def resolve_virtual_disk_block_number(self,disk_number,block_number):
        
        disk_id = self.resolve_disk_number(disk_number)
        if disk_id==-1:
            return -1
        disk_size = 0        
        for i in self.disk_dictionary[disk_id]:
            disk_size += i[1]-i[0]+1
        if block_number<=0 or block_number>disk_size:
            return -1
        
        print(disk_id)
        
        block_number -= 1
        for i in self.disk_dictionary[disk_id]:
            if i[1]-i[0] < block_number:
                block_number -= i[1]-i[0]+1
            else:
                block_number += i[0]
                return block_number
        
    def read_virtual_disk_data(self,disk_number,block_number):
        
        block_number = self.resolve_virtual_disk_block_number(disk_number,block_number+1)
        if block_number == -1:
            return -1
        print(block_number)
        return self.read_block_data(block_number)
    
    def write_virtual_disk_data(self,disk_number,block_number,block_information):
        
        block_number = self.resolve_virtual_disk_block_number(disk_number,block_number+1)
        if block_number == -1:
            return -1
        print(block_number)
        return self.write_block_data(block_number,block_information)

class virtual_snapshot_storage_system(virtual_storage_system):
    
    def __init__(self):
        super().__init__()
        self.backup_metadata = []
        
    def get_backup_name(self):
        print('Choose the version that you wish to restore your system to:')
        for (backup_number,backup_name) in enumerate(self.backup_metadata):
            print(backup_number+1,backup_name)
        backup_number = int(input())
        if backup_number>0 and backup_number<=len(self.backup_metadata):
            return self.backup_metadata[backup_number-1]
        else:
            print('Please enter a correct number:')
            return self.get_backup_name()
        
    def create_backup(self):
        backup_name = str(datetime.now())[:-4].replace(':','-').replace('.','-')
        self.backup_metadata.append(backup_name)
        file = open(backup_name,'wb')
        current_state = [self.disk_dictionary,self.space_list,self.space_available,self.next_available_id,self.disk_A_data,self.disk_A_metadata,self.disk_B_data,self.disk_B_metadata]
        pickle.dump(current_state,file)
        file.close()
        return backup_name
        
    def restore_backup(self):
        backup_name = self.get_backup_name()
        file = open(backup_name,'rb')
        current_state = pickle.load(file)
        [self.disk_dictionary,self.space_list,self.space_available,self.next_available_id,self.disk_A_data,self.disk_A_metadata,self.disk_B_data,self.disk_B_metadata] = current_state
        file.close()
        return backup_name

class question1:
    def __init__(self):
        self.main_storage_system = virtual_storage_system()
        
    def run(self):
        while(True):
            print(self.main_storage_system.disk_dictionary,self.main_storage_system.space_list,sep='\n')
            print('\n******************************************')
            print('Choose:')
            print('1. Display all the current virtual disks.')
            print('2. Create a virtual disk.')
            print('3. Delete a virtual disk.')
            print('4. Read from a virtual disk.')
            print('5. Write data to a virtual disk.')
            print('6. Read data directly from a disk block.')
            print('7. Write data directly to a disk block.')
            print('9. Exit')
            print('******************************************\n')
            option = int(input('Enter your option : '))
            if option==1:
                self.main_storage_system.display_virtual_disks_names()
            elif option==2:
                size = int(input('Enter the size of the new virtual disk : '))
                value = self.main_storage_system.create_disk(size)
                if value==-1:
                    print('Unable to create the virtual disk. Error!')
                else:
                    print('Virtual disk',value,'created!')
            elif option==3:
                disk_number = int(input('Enter the virtual disk number : '))
                disk_id = list(self.main_storage_system.disk_dictionary.keys())[disk_number-1]
                value = self.main_storage_system.delete_disk(disk_id)
                if value==-1:
                    print('Unable to delete the virtual disk. Error!')
                else:
                    print('Virtual disk \''+value+'\' deleted!')
            elif option==4:
                disk_number = int(input('Enter the virtual disk number : '))
                block_number = int(input('Enter the virtual disk block number : '))
                value = self.main_storage_system.read_virtual_disk_data(disk_number,block_number)
                if value==-1:
                    print('Unable to read from the virtual disk. Error!')
                else:
                    print('Data present in the block :\n'+value)
            elif option==5:
                disk_number = int(input('Enter the virtual disk number : '))
                block_number = int(input('Enter the virtual disk block number : '))
                block_info = input('Enter the info to be written : ')
                value = self.main_storage_system.write_virtual_disk_data(disk_number,block_number,str(block_info))
                if value==-1:
                    print('Unable to write to the virtual disk. Error!')
                else:
                    print('Data successfully written to the disk.')
            elif option==6:
                block_number = int(input('Enter a block number between 1-500 : '))
                if block_number>=1 and block_number<=500:
                    value = self.main_storage_system.read_block_data(block_number)
                    print('Data present in the block :\n'+value)
                else:
                    print('Please enter a correct block number. Error!')
            elif option==7:
                block_number = int(input('Enter a block number between 1-500 : '))
                if block_number>=1 and block_number<=500:
                    block_info = input('Enter the information to be entered into the block : ')
                    self.main_storage_system.write_block_data(block_number,block_info)
                    print('Data written to the desired block.')
                else:
                    print('Please enter a correct block number. Error!')
                
            elif option==9:
                break
            else:
                print('Please enter a valid option.')

class question2:
    def __init__(self):
        self.main_storage_system = virtual_storage_system()
        self.duplicate_storage_system_1 = virtual_storage_system()
        self.duplicate_storage_system_2 = virtual_storage_system()
        self.corrupted_blocks = set()
        
    def run(self):
        while(True):
            print(self.main_storage_system.disk_dictionary,self.main_storage_system.space_list,self.corrupted_blocks,sep='\n')
            print('\n******************************************')
            print('Choose:')
            print('1. Display all the current virtual disks.')
            print('2. Create a virtual disk.')
            print('3. Delete a virtual disk.')
            print('4. Read from a virtual disk.')
            print('5. Write data to a virtual disk.')
            print('9. Exit')
            print('******************************************\n')
            option = int(input('Enter your option : '))
            if option==1:
                self.main_storage_system.display_virtual_disks_names()
            elif option==2:
                size = int(input('Enter the size of the new virtual disk : '))
                value = self.main_storage_system.create_disk(size)
                if value==-1:
                    print('Unable to create the virtual disk. Error!')
                else:
                    self.duplicate_storage_system_1.create_disk(size)
                    print('Virtual disk',value,'created!')
            elif option==3:
                disk_number = int(input('Enter the virtual disk number : '))
                disk_id = list(self.main_storage_system.disk_dictionary.keys())[disk_number-1]
                value = self.main_storage_system.delete_disk(disk_id)
                if value==-1:
                    print('Unable to delete the virtual disk. Error!')
                else:
                    temp_list = []
                    for i in self.corrupted_blocks:
                        if i[0] == disk_number:
                            temp_list.append(i)
                    for i in temp_list:
                        self.corrupted_blocks.remove(i)
                    self.duplicate_storage_system_1.delete_disk(disk_id)
                    print('Virtual disk \''+value+'\' deleted!')
            elif option==4:
                disk_number = int(input('Enter the virtual disk number : '))
                block_number = int(input('Enter the virtual disk block number : '))
                random_number = random.randint(1,101)
                if random_number>10:
                    if (disk_number,block_number,_) in self.corrupted_blocks:
                        value = self.duplicate_storage_system_1.read_virtual_disk_data(disk_number,block_number)
                    else:
                        value = self.main_storage_system.read_virtual_disk_data(disk_number,block_number)
                    if value==-1:
                        print('Unable to read from the virtual disk. Error!')
                    else:
                        print('Data present in the block :\n'+value)
                else:
                    value = self.duplicate_storage_system_1.read_virtual_disk_data(disk_number,block_number)
                    if (disk_number,block_number) not in self.corrupted_blocks:
                        temp_value = self.main_storage_system.resolve_virtual_disk_block_number(disk_number,block_number+1)
                        self.duplicate_storage_system_2.write_block_data(temp_value,block_info)
                        self.corrupted_blocks.add((disk_number,block_number,temp_value))
                    if value==-1:
                        print('Unable to read from the virtual disk. Error!')
                    else:
                        print('Data present in the duplicated block :\n'+value)
                    
            elif option==5:
                disk_number = int(input('Enter the virtual disk number : '))
                block_number = int(input('Enter the virtual disk block number : '))
                block_info = input('Enter the info to be written : ')
                random_number = random.randint(1,101)
                if random_number>10:
                    if (disk_number,block_number,_) in self.corrupted_blocks:
                        print('******')
                        value = self.duplicate_storage_system_1.write_virtual_disk_data(disk_number,block_number,str(block_info))
                        temp_value = self.main_storage_system.resolve_virtual_disk_block_number(disk_number,block_number+1)
                        self.duplicate_storage_system_2.write_block_data(temp_value,block_info)
                    else:
                        print('######')
                        value = self.main_storage_system.write_virtual_disk_data(disk_number,block_number,str(block_info))
                        self.duplicate_storage_system_1.write_virtual_disk_data(disk_number,block_number,str(block_info))
                    if value==-1:
                        print('Unable to write to the virtual disk. Error!')
                    else:
                        print('Data written in the virtual disk.')
                else:
                    print('1231232123123132')
                    value = self.duplicate_storage_system_1.write_virtual_disk_data(disk_number,block_number,str(block_info))
                    temp_value = self.main_storage_system.resolve_virtual_disk_block_number(disk_number,block_number+1)
                    self.duplicate_storage_system_2.write_block_data(temp_value,block_info)
                    if (disk_number,block_number) not in self.corrupted_blocks:
                        temp_value = resolve_virtual_disk_block_number(disk_number,block_number)
                        self.corrupted_blocks.add((disk_number,block_number,temp_value))
                    if value==-1:
                        print('Unable to write to the virtual disk. Error!')
                    else:
                        print('Data written in the virtual disk.')
            elif option==9:
                break
            else:
                print('Please enter a valid option.')

class question3:
    def __init__(self):
        self.main_storage_system = virtual_snapshot_storage_system()
        
    def run(self):
        while(True):
            print(self.main_storage_system.disk_dictionary,self.main_storage_system.space_list,sep='\n')
            print('\n******************************************')
            print('Choose:')
            print('1. Display all the current virtual disks.')
            print('2. Create a virtual disk.')
            print('3. Delete a virtual disk.')
            print('4. Read from a virtual disk.')
            print('5. Write data to a virtual disk.')
            print('6. Read data directly from a disk block.')
            print('7. Write data directly to a disk block.')
            print('8. Create a backup of the virtual machines.')
            print('9. Restore the system to a specific checkpoint.')
            print('0. Exit')
            print('******************************************\n')
            option = int(input('Enter your option : '))
            if option==1:
                self.main_storage_system.display_virtual_disks_names()
            elif option==2:
                size = int(input('Enter the size of the new virtual disk : '))
                value = self.main_storage_system.create_disk(size)
                if value==-1:
                    print('Unable to create the virtual disk. Error!')
                else:
                    print('Virtual disk',value,'created!')
            elif option==3:
                disk_number = int(input('Enter the virtual disk number : '))
                disk_id = list(self.main_storage_system.disk_dictionary.keys())[disk_number-1]
                value = self.main_storage_system.delete_disk(disk_id)
                if value==-1:
                    print('Unable to delete the virtual disk. Error!')
                else:
                    print('Virtual disk \''+value+'\' deleted!')
            elif option==4:
                disk_number = int(input('Enter the virtual disk number : '))
                block_number = int(input('Enter the virtual disk block number : '))
                value = self.main_storage_system.read_virtual_disk_data(disk_number,block_number)
                if value==-1:
                    print('Unable to read from the virtual disk. Error!')
                else:
                    print('Data present in the block :\n'+value)
            elif option==5:
                disk_number = int(input('Enter the virtual disk number : '))
                block_number = int(input('Enter the virtual disk block number : '))
                block_info = input('Enter the info to be written : ')
                value = self.main_storage_system.write_virtual_disk_data(disk_number,block_number,str(block_info))
                if value==-1:
                    print('Unable to write to the virtual disk. Error!')
                else:
                    print('Data successfully written to the disk.')
            elif option==6:
                block_number = int(input('Enter a block number between 1-500 : '))
                if block_number>=1 and block_number<=500:
                    value = self.main_storage_system.read_block_data(block_number)
                    print('Data present in the block :\n'+value)
                else:
                    print('Please enter a correct block number. Error!')
            elif option==7:
                block_number = int(input('Enter a block number between 1-500 : '))
                if block_number>=1 and block_number<=500:
                    block_info = input('Enter the information to be entered into the block : ')
                    self.main_storage_system.write_block_data(block_number,block_info)
                    print('Data written to the desired block.')
                else:
                    print('Please enter a correct block number. Error!')
            elif option==8:
                print('Backup name: '+self.main_storage_system.create_backup()+'. Created Successfully.')
            elif option==9:
                backup_name = self.main_storage_system.restore_backup()
                print('Successfully restored to:'+backup_name+'.')
            elif option==0:
                break
            else:
                print('Please enter a valid option.')

print('1. Question1\n2. Question2\n3. Question3')
option = int(input('Enter which part you wish to run : '))
if option==1:
    question1().run()
elif option==2:
    question2().run()
elif option==3:
    question3().run()
else:
    print('Invalid option.')