#### Need to redo the last part
setwd("C:/Users/yinghong/Desktop/Spring 2019/562/Project 3")

library(data.table)
library(caret)
library(dplyr)
library(lubridate)


data=fread("alldata.csv")

#create new risk table variable

data$DayofWeek=wday(data$date,label=TRUE)
data$DayofMonth=substr(data$date, start= 9,stop=10)

#separate training and testing
train=data[1:833507,]
test=data[833508:1000000,]


y=train$fraud_label  ## storing in y

fea=c("DayofWeek","DayofMonth")
fea

train[[fea[1]]]

tr=train
ts=test

for (i in fea)
{
  col <- data.frame("predictor" = train[[i]], "target" = y)
  col_ts<- data.frame("predictor" = test[[i]])
  
  lookup = col %>% 
    group_by(predictor) %>%
    summarise(mean_target = mean(target))
  
  col = left_join(col, lookup)
  col_ts = left_join(col_ts, lookup)
  
  tr[[i]] <- col$mean_target
  ts[[i]] <- col_ts$mean_target
}


write.csv(tr, 'risk_table.csv',row.names = FALSE)
