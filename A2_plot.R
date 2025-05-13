library(readr)
library(ggplot2)
library(dplyr)
library(ggthemr)


area <- c(3194.08, 21376.38, 41202.27, 7848.43, 4387.55, 724.1, 7.54)
names <- c('Enhanced Regrowth', 'Enhanced Growth', 'Unburned', 'Low Severity', 'Moderate-Low Severity', 'Moderate-High Severity', 'High Severity')


severity <- data.frame(Severity = names, Area = area)

ggthemr('grape')

ggplot(severity, aes(x = reorder(Severity, +area), y = Area)) +
  geom_col(show.legend = F) +
  coord_flip() +
  ggtitle("Burn Severity and Area Impacted by Wildfire in Shelburne County Nova Scotia 2023") +
  ylab('Area (Ha)') +
  xlab('Severity') +
  theme(plot.title= element_text(hjust=0.5, size=14)) +
  geom_label(aes(label = Area), alpha=0.5)



