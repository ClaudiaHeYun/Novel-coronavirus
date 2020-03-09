# Initialize libraries
required_packages <- c("dplyr", "ggpubr", "ez", "effects", "psych", "lme4", "ggplot2") # list of packages required

# Check if any listed packages are not installed
new_packages <- required_packages[!(required_packages %in% installed.packages()[,"Package"])]

# Install packages_new if it’s not empty
if(length(new_packages)) install.packages(new_packages)
install.packages("readxl")
install.packages("unite")
install.packages("sjmisc")

# Load packages
lapply(required_packages, library, character.only = TRUE)
library(readxl)
library(tidyr)
library(sjmisc)


### SET WORKING DIRECTORY

### will update later, just don't want to accidentally delete something
setwd("C:/Users/zevan/Documents/Classes/Data Science/coronavirus") #for use on my pc
#not sure how this works in github

###Reading in Databases
original = read.csv("rawInfections.csv")
locations = as.character(original[[1]])
for (i in (1:(length(locations))))
{
  if (str_contains(locations[[i]], ',')) {
    result = strsplit(locations[[i]], ', ')
    locations[i] = result[[1]][[2]]
#    locations[i] = result[2]
  }
}
data = original
data[1] = locations

### cleaning bits
#original <- original[, -c(2:6)]
#original <- original %>%
#  rename(
#    ID = subDirectory_filePath
#  )


write.csv(data, file = "cleanedData.csv")
