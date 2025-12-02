import time
t = int(input("focus  minutes:")) * 60
start = time.time()
print("focus started.......")
time.sleep(t)
end=time.time()
print("Done! Focused for", round((end-start)/60,1),"minutes.")