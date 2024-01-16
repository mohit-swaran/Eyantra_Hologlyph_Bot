# Assume you have a list
my_list = [1, 2, 3, 4, 5]

# Iterate through the list using range and len
for i in range(len(my_list)):
    print(my_list[i])

    # Check if the current index is the last one
    if i == len(my_list) - 1:
        print("End of the list")