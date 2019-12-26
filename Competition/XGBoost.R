library(timeDate)
library(dplyr)
library(forecast)
library(readxl)
library(lubridate)
library(MLmetrics)
library(ggplot2)
library(xgboost)
library(tidyverse) # data manipulation
library(mlr)       # ML package (also some data manipulation)
library(knitr)     # just using this for kable() to make pretty tables
library(gbm)

###Data Preperation
#data<- read.csv("Train.csv")
data=read_excel("201908 UNC vs USC(1).xlsx")

data=data%>%mutate(Temperature2=data$Temperature^2,
              Temperature3=data$Temperature^3)

data=data[ ,!(colnames(data) =='Predicted Load')]

data$Date=as.Date(data$Date,format='%d-%b-%y')

data$Month=month(data$Date)
data$Weekday=wday(data$Date,label=TRUE)
data$Week=week(data$Date)




holidaylist=c(
  "USNewYearsDay", 
  "USMemorialDay", 
  "USIndependenceDay", 
  "USLaborDay", 
  "USElectionDay", 
  "USThanksgivingDay", 
  "USChristmasDay", 
  "USCPulaskisBirthday", 
  "USGoodFriday"
)


######
hdl=NULL
hd=NULL

for (y in seq(2008,2011)){
  for (h in holidaylist){
    hdl=c(hdl,h)
    hd=c(hd,holiday(y,h))
  }
}

hd=t(as.data.frame(hd))
hdl=as.data.frame(hdl)
holiday=cbind(hdl,hd)
names(holiday)=c("Holiday","Date")
holiday$Date=as.Date(holiday$Date)

##################
##Regression with Month, Weekday, Holiday
##Holiday as columns

lm_data=left_join(data,holiday,by="Date")
lm_data$Holiday=as.character(lm_data$Holiday)
lm_data$Holiday[is.na(lm_data$Holiday)] <- "Not Holiday"

##Regression
#Convert categorical variables into factor
lm_data$Hour=as.factor(lm_data$Hour)
lm_data$Weekday=as.factor(lm_data$Weekday)
lm_data$Month=as.factor(lm_data$Month)
lm_data$Holiday=as.factor(lm_data$Holiday)
lm_data$Week=as.factor(lm_data$Week)

#Without Lag
tra=lm_data[lm_data$Date<'2011-01-01',]
tes=lm_data[lm_data$Date>='2011-01-01' & lm_data$Date<'2012-01-01',]

###############
#XGBoost
x_train=tra[ ,!(colnames(tra) %in% c("Load","Date"))]
y_train=tra[,"Load"]
x_test=tes[ ,!(colnames(tra) %in% c("Load","Date"))]
y_test=tes[,"Load"]

#1. Default Parameter
dtrain=xgb.DMatrix(data.matrix(x_train), label=tra$Load)
dtest=xgb.DMatrix(data.matrix(x_test), label=tes$Load)

fit_xgb1 <- xgboost(dtrain
                   , max_depth = 10
                   , eta = 0.02
                   , nthread = 2
                   , nrounds = 800
                   , booster = "gbtree"
                   , objective="reg:linear")

y_hat_xgb1 <- predict(fit_xgb1,data.matrix(x_test))
MAPE(y_pred=y_hat_xgb1,y_true=data.matrix(y_test))
#3.56%



plot(data.matrix(y_test),data.matrix(y_test)-y_hat_xgb1,
     main="Residual Plot")

#####CV
#2. eta=0.1
fit_xgb2 <- xgboost(dtrain
                    , max_depth = 10
                    , eta = 0.1
                    , nthread = 2
                    , nrounds = 800
                    , booster = "gbtree"
                    , objective="reg:linear")

y_hat_xgb2 <- predict(fit_xgb2, data.matrix(x_test))

MAPE(y_pred=y_hat_xgb2,y_true=data.matrix(y_test))

#3.83%

##########
gbm1= gbm(Load~Temperature+Temperature2+Temperature3
          +Weekday+Month+Week+Hour+Holiday-Date,
                       data = tra, n.trees = 10000,
                       shrinkage = 0.01, interaction.depth = 4)

y_gbm <- predict(gbm1, x_test,n.trees=10000)


MAPE(y_pred=y_gbm,y_true=data.matrix(y_test))
#3.47%
plot(data.matrix(y_test),data.matrix(y_test)-y_gbm,
     main="Residual Plot for gbm")

plot(y=data.matrix(y_test)-y_gbm,x=tes$Date,type='l')

#make prediction for 2012
x_predict=lm_data[lm_data$Date>='2012-01-01',!colnames(lm_data)=='Load']
y_predict=predict(gbm1, x_predict,n.trees=10000)

result=c(predict(gbm1, x_train,n.trees=10000),
             predict(gbm1, x_test,n.trees=10000),
             predict(gbm1, x_predict,n.trees=10000))

write.csv(result,'prediction.csv')
predict(gbm1, x_train,n.trees=10000)
predict(gbm1, x_test,n.trees=10000)
predict(gbm1, x_predict,n.trees=10000)
