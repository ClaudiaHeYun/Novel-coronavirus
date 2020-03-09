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
original = read.csv("raw_infections.csv")
sliced = original[-c(14, 57, 70, 220:225), -c(3, 7, 8)]
locations = as.character(sliced[[1]])
for (i in (1:(length(locations))))
{
  if (str_contains(locations[[i]], ',')) {
    result = strsplit(locations[[i]], ', ')
    locations[i] = result[[1]][[2]]
  }
}
data = sliced
data[1] = locations

dat = unite(data, comb_place, c(Province.State, Country.Region), sep = "/")

k = length(dat[,1])
h = k
for (i in (1:k)) {
  for (j in (1:k)) {
    if (i < h && j < h) {
      if ((dat[i, 1] == dat[j, 1]) && (i != j)){
        dat[i, 3] = dat[i, 3] + dat[j, 3]
        dat[i, 4] = dat[i, 4] + dat[j, 4]
        dat[i, 2] = dat[i, 2] + dat[j, 2]
        dat = dat[-j, ]
        h = h-1
      }
    }
  }
}

state = as.character(dat[[1]])
country = as.character(dat[[1]])
for (i in (1:(length(state))))
{
  result = strsplit(state[[i]], '/')
  state[i] = result[[1]][[1]]
  country[i] = result[[1]][[2]]
}


collapsed = dat
collapsed$state = state
collapsed$country = country
collapsed = collapsed[-1]

write.csv(collapsed, file = "cleaned_infections.csv")
