from PIL import Image
import numpy as np
import matplotlib.pyplot as plt

image = Image.open("image9.jpg")
imageData = np.asarray(image)


#row, col = np.mgrid[0:imageData.shape[0], 0:imageData.shape[1]]

outputImage = np.zeros((imageData.shape[0], imageData.shape[1]))

#print("test")

for row in range(imageData.shape[0]):
    for col in range(imageData.shape[1]):
        red = int(imageData[row][col][0])
        blue = int(imageData[row][col][2])

        outputImage[row][col] = (red - blue)/(red + blue)

fig, ax = plt.subplots(1,1)
im = ax.imshow(outputImage)
fig.colorbar(im)
plt.savefig("output7.jpg")





