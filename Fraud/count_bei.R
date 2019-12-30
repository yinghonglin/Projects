
library(data.table)
library(lubridate)
library(dplyr)

data=read.csv("applications_processed.csv")
data$date=ymd(data$date)

data$namedob=paste(data$firstname,data$lastname,data$dob,sep="_")
data$fulladdress=paste(data$address,data$zip5,sep="_")

train2=data

setDT(train2)
# Define a function to implement time-interval join in data.table
timeWinJoin = function(dt, n, byVar){
  dt1 = dt
  # Generate duplicated copy for the columns we'll join on
  # as they'll disappear after running the data.table join method,
  # n is the length of the time window
  dt1$join_ts1 = dt1$date
  dt1$join_ts2 = dt1$date + n
  dt1$join_rec = dt1$record
  # The join conditions below are equivalent to what in the sqldf code
  keys = c(byVar, 'join_ts1<=date', 'join_ts2>=date', 'record<=record')
  dt2 = dt1[dt, on=keys, allow.cartesian=T]
  return(dt2)
}

for (i in c(0,1,3,7,14,30)){
  for (j in c("ssn","fulladdress","namedob","homephone")){
    assign(paste0("dt",j,i), timeWinJoin(train2, i, j))
  }
}

for (i in c(0,1,3,7,14,30)){
  for (j in list(c('ssn','fulladdress'),c('ssn','namedob'),c('ssn','homephone'))){
    assign(paste0("dt",j[1],j[2],i), timeWinJoin(train2, i, j))
  }
}

for (i in c(0,1,3,7,14,30)){
  for (j in list(c('fulladdress','namedob'),c('fulladdress','homephone'),c('namedob','homephone'))){
    assign(paste0("dt",j[1],j[2],i), timeWinJoin(train2, i, j))
  }
}

for (i in c(0,1,3,7,14,30)){
  for (j in list(c('firstname','ssn'),c('lastname','ssn'),c('firstname','fulladdress'),c('lastname','fulladdress'))){
    assign(paste0("dt",j[1],j[2],i), timeWinJoin(train2, i, j))
  }
}

dtfulladdress0c <- dtfulladdress0[, .(
  count = .N),
  by=record]

dtfulladdress1c <- dtfulladdress1[, .(
  count = .N),
  by=record]

dtfulladdress3c <- dtfulladdress3[, .(
  count = .N),
  by=record]

dtfulladdress7c <- dtfulladdress7[, .(
  count = .N),
  by=record]

dtfulladdress14c <- dtfulladdress14[, .(
  count = .N),
  by=record]

dtfulladdress30c <- dtfulladdress30[, .(
  count = .N),
  by=record]

dthomephone0c <- dthomephone0[, .(
  count = .N),
  by=record]

dthomephone1c <- dthomephone1[, .(
  count = .N),
  by=record]

dthomephone3c <- dthomephone3[, .(
  count = .N),
  by=record]

dthomephone7c <- dthomephone7[, .(
  count = .N),
  by=record]

dthomephone14c <- dthomephone14[, .(
  count = .N),
  by=record]

dthomephone30c <- dthomephone30[, .(
  count = .N),
  by=record]

dtnamedob0c <- dtnamedob0[, .(
  count = .N),
  by=record]

dtnamedob1c <- dtnamedob1[, .(
  count = .N),
  by=record]

dtnamedob3c <- dtnamedob3[, .(
  count = .N),
  by=record]

dtnamedob7c <- dtnamedob7[, .(
  count = .N),
  by=record]

dtnamedob14c <- dtnamedob14[, .(
  count = .N),
  by=record]

dtnamedob30c <- dtnamedob30[, .(
  count = .N),
  by=record]

dtssn0c <- dtssn0[, .(
  count = .N),
  by=record]

dtssn1c <- dtssn1[, .(
  count = .N),
  by=record]

dtssn3c <- dtssn3[, .(
  count = .N),
  by=record]

dtssn7c <- dtssn7[, .(
  count = .N),
  by=record]

dtssn14c <- dtssn14[, .(
  count = .N),
  by=record]

dtssn30c <- dtssn30[, .(
  count = .N),
  by=record]

dtssnfulladdress0c <- dtssnfulladdress0[, .(
  count = .N),
  by=record]

dtssnfulladdress1c <- dtssnfulladdress1[, .(
  count = .N),
  by=record]

dtssnfulladdress3c <- dtssnfulladdress3[, .(
  count = .N),
  by=record]

dtssnfulladdress7c <- dtssnfulladdress7[, .(
  count = .N),
  by=record]

dtssnfulladdress14c <- dtssnfulladdress14[, .(
  count = .N),
  by=record]

dtssnfulladdress30c <- dtssnfulladdress30[, .(
  count = .N),
  by=record]

dtssnhomephone0c <- dtssnhomephone0[, .(
  count = .N),
  by=record]

dtssnhomephone1c <- dtssnhomephone1[, .(
  count = .N),
  by=record]

dtssnhomephone3c <- dtssnhomephone3[, .(
  count = .N),
  by=record]

dtssnhomephone7c <- dtssnhomephone7[, .(
  count = .N),
  by=record]

dtssnhomephone14c <- dtssnhomephone14[, .(
  count = .N),
  by=record]

dtssnhomephone30c <- dtssnhomephone30[, .(
  count = .N),
  by=record]

dtssnnamedob0c <- dtssnnamedob0[, .(
  count = .N),
  by=record]

dtssnnamedob1c <- dtssnnamedob1[, .(
  count = .N),
  by=record]

dtssnnamedob3c <- dtssnnamedob3[, .(
  count = .N),
  by=record]

dtssnnamedob7c <- dtssnnamedob7[, .(
  count = .N),
  by=record]

dtssnnamedob14c <- dtssnnamedob14[, .(
  count = .N),
  by=record]

dtssnnamedob30c <- dtssnnamedob30[, .(
  count = .N),
  by=record]

dtfulladdressnamedob0c <- dtfulladdressnamedob0[, .(
  count = .N),
  by=record]

dtfulladdressnamedob1c <- dtfulladdressnamedob1[, .(
  count = .N),
  by=record]

dtfulladdressnamedob3c <- dtfulladdressnamedob3[, .(
  count = .N),
  by=record]

dtfulladdressnamedob7c <- dtfulladdressnamedob7[, .(
  count = .N),
  by=record]

dtfulladdressnamedob14c <- dtfulladdressnamedob14[, .(
  count = .N),
  by=record]

dtfulladdressnamedob30c <- dtfulladdressnamedob30[, .(
  count = .N),
  by=record]

dtfulladdresshomephone0c <- dtfulladdresshomephone0[, .(
  count = .N),
  by=record]

dtfulladdresshomephone1c <- dtfulladdresshomephone1[, .(
  count = .N),
  by=record]

dtfulladdresshomephone3c <- dtfulladdresshomephone3[, .(
  count = .N),
  by=record]

dtfulladdresshomephone7c <- dtfulladdresshomephone7[, .(
  count = .N),
  by=record]

dtfulladdresshomephone14c <- dtfulladdresshomephone14[, .(
  count = .N),
  by=record]

dtfulladdresshomephone30c <- dtfulladdresshomephone30[, .(
  count = .N),
  by=record]

dtnamedobhomephone0c <- dtnamedobhomephone0[, .(
  count = .N),
  by=record]

dtnamedobhomephone1c <- dtnamedobhomephone1[, .(
  count = .N),
  by=record]

dtnamedobhomephone3c <- dtnamedobhomephone3[, .(
  count = .N),
  by=record]

dtnamedobhomephone7c <- dtnamedobhomephone7[, .(
  count = .N),
  by=record]

dtnamedobhomephone14c <- dtnamedobhomephone14[, .(
  count = .N),
  by=record]

dtnamedobhomephone30c <- dtnamedobhomephone30[, .(
  count = .N),
  by=record]

dtfirstnamessn0c <- dtfirstnamessn0[, .(
  count = .N),
  by=record]

dtfirstnamessn1c <- dtfirstnamessn1[, .(
  count = .N),
  by=record]

dtfirstnamessn3c <- dtfirstnamessn3[, .(
  count = .N),
  by=record]

dtfirstnamessn7c <- dtfirstnamessn7[, .(
  count = .N),
  by=record]

dtfirstnamessn14c <- dtfirstnamessn14[, .(
  count = .N),
  by=record]

dtfirstnamessn30c <- dtfirstnamessn30[, .(
  count = .N),
  by=record]

dtlastnamessn0c <- dtlastnamessn0[, .(
  count = .N),
  by=record]

dtlastnamessn1c <- dtlastnamessn1[, .(
  count = .N),
  by=record]

dtlastnamessn3c <- dtlastnamessn3[, .(
  count = .N),
  by=record]

dtlastnamessn7c <- dtlastnamessn7[, .(
  count = .N),
  by=record]

dtlastnamessn14c <- dtlastnamessn14[, .(
  count = .N),
  by=record]

dtlastnamessn30c <- dtlastnamessn30[, .(
  count = .N),
  by=record]

dtfirstnamefulladdress0c <- dtfirstnamefulladdress0[, .(
  count = .N),
  by=record]

dtfirstnamefulladdress1c <- dtfirstnamefulladdress1[, .(
  count = .N),
  by=record]

dtfirstnamefulladdress3c <- dtfirstnamefulladdress3[, .(
  count = .N),
  by=record]

dtfirstnamefulladdress7c <- dtfirstnamefulladdress7[, .(
  count = .N),
  by=record]

dtfirstnamefulladdress14c <- dtfirstnamefulladdress14[, .(
  count = .N),
  by=record]

dtfirstnamefulladdress30c <- dtfirstnamefulladdress30[, .(
  count = .N),
  by=record]

dtlastnamefulladdress0c <- dtlastnamefulladdress0[, .(
  count = .N),
  by=record]

dtlastnamefulladdress1c <- dtlastnamefulladdress1[, .(
  count = .N),
  by=record]

dtlastnamefulladdress3c <- dtlastnamefulladdress3[, .(
  count = .N),
  by=record]

dtlastnamefulladdress7c <- dtlastnamefulladdress7[, .(
  count = .N),
  by=record]

dtlastnamefulladdress14c <- dtlastnamefulladdress14[, .(
  count = .N),
  by=record]

dtlastnamefulladdress30c <- dtlastnamefulladdress30[, .(
  count = .N),
  by=record]

alldata=data.table(train2,dtfulladdress0c[,2],dtfulladdress1c[,2],dtfulladdress3c[,2],
                   dtfulladdress7c[,2],dtfulladdress14c[,2],dtfulladdress30c[,2],
                   dthomephone0c[,2],dthomephone1c[,2],dthomephone3c[,2],
                   dthomephone7c[,2],dthomephone14c[,2],dthomephone30c[,2],
                   dtnamedob0c[,2],dtnamedob1c[,2],dtnamedob3c[,2],
                   dtnamedob7c[,2],dtnamedob14c[,2],dtnamedob30c[,2],
                   dtssn0c[,2],dtssn1c[,2],dtssn3c[,2],
                   dtssn7c[,2],dtssn14c[,2],dtssn30c[,2],
                   dtssnfulladdress0c[,2],dtssnfulladdress1c[,2],dtssnfulladdress3c[,2],
                   dtssnfulladdress7c[,2],dtssnfulladdress14c[,2],dtssnfulladdress30c[,2],
                   dtssnhomephone0c[,2],dtssnhomephone1c[,2],dtssnhomephone3c[,2],
                   dtssnhomephone7c[,2],dtssnhomephone14c[,2],dtssnhomephone30c[,2],
                   dtssnnamedob0c[,2],dtssnnamedob1c[,2],dtssnnamedob3c[,2],
                   dtssnnamedob7c[,2],dtssnnamedob14c[,2],dtssnnamedob30c[,2],
                   dtfulladdressnamedob0c[,2],dtfulladdressnamedob1c[,2],dtfulladdressnamedob3c[,2],
                   dtfulladdressnamedob7c[,2],dtfulladdressnamedob14c[,2],dtfulladdressnamedob30c[,2],
                   dtfulladdresshomephone0c[,2],dtfulladdresshomephone1c[,2],dtfulladdresshomephone3c[,2],
                   dtfulladdresshomephone7c[,2],dtfulladdresshomephone14c[,2],dtfulladdresshomephone30c[,2],
                   dtnamedobhomephone0c[,2],dtnamedobhomephone1c[,2],dtnamedobhomephone3c[,2],
                   dtnamedobhomephone7c[,2],dtnamedobhomephone14c[,2],dtnamedobhomephone30c[,2],
                   dtfirstnamessn0c[,2],dtfirstnamessn1c[,2],dtfirstnamessn3c[,2],
                   dtfirstnamessn7c[,2],dtfirstnamessn14c[,2],dtfirstnamessn30c[,2],
                   dtlastnamessn0c[,2],dtlastnamessn1c[,2],dtlastnamessn3c[,2],
                   dtlastnamessn7c[,2],dtlastnamessn14c[,2],dtlastnamessn30c[,2],
                   dtfirstnamefulladdress0c[,2],dtfirstnamefulladdress1c[,2],dtfirstnamefulladdress3c[,2],
                   dtfirstnamefulladdress7c[,2],dtfirstnamefulladdress14c[,2],dtfirstnamefulladdress30c[,2],
                   dtlastnamefulladdress0c[,2],dtlastnamefulladdress1c[,2],dtlastnamefulladdress3c[,2],
                   dtlastnamefulladdress7c[,2],dtlastnamefulladdress14c[,2],dtlastnamefulladdress30c[,2])

colnames(alldata)=c(colnames(alldata)[1:13],'fulladdress_0_count','fulladdress_1_count','fulladdress_3_count',
                    'fulladdress_7_count','fulladdress_14_count','fulladdress_30_count',
                    'homephone_0_count','homephone_1_count','homephone_3_count',
                    'homephone_7_count','homephone_14_count','homephone_30_count',
                    'namedob_0_count','namedob_1_count','namedob_3_count',
                    'namedob_7_count','namedob_14_count','namedob_30_count',
                    'ssn_0_count','ssn_1_count','ssn_3_count',
                    'ssn_7_count','ssn_14_count','ssn_30_count',
                    'ssnfulladdress_0_count','ssnfulladdress_1_count','ssnfulladdress_3_count',
                    'ssnfulladdress_7_count','ssnfulladdress_14_count','ssnfulladdress_30_count',
                    'ssnhomephone_0_count','ssnhomephone_1_count','ssnhomephone_3_count',
                    'ssnhomephone_7_count','ssnhomephone_14_count','ssnhomephone_30_count',
                    'ssnnamedob_0_count','ssnnamedob_1_count','ssnnamedob_3_count',
                    'ssnnamedob_7_count','ssnnamedob_14_count','ssnnamedob_30_count',
                    'fulladdressnamedob_0_count','fulladdressnamedob_1_count','fulladdressnamedob_3_count',
                    'fulladdressnamedob_7_count','fulladdressnamedob_14_count','fulladdressnamedob_30_count',
                    'fulladdresshomephone_0_count','fulladdresshomephone_1_count','fulladdresshomephone_3_count',
                    'fulladdresshomephone_7_count','fulladdresshomephone_14_count','fulladdresshomephone_30_count',
                    'namedobhomephone_0_count','namedobhomephone_1_count','namedobhomephone_3_count',
                    'namedobhomephone_7_count','namedobhomephone_14_count','namedobhomephone_30_count',
                    'firstnamessn_0_count','firstnamessn_1_count','firstnamessn_3_count',
                    'firstnamessn_7_count','firstnamessn_14_count','firstnamessn_30_count',
                    'lastnamessn_0_count','lastnamessn_1_count','lastnamessn_3_count',
                    'lastnamessn_7_count','lastnamessn_14_count','lastnamessn_30_count',
                    'firstnamefulladdress_0_count','firstnamefulladdress_1_count','firstnamefulladdress_3_count',
                    'firstnamefulladdress_7_count','firstnamefulladdress_14_count','firstnamefulladdress_30_count',
                    'lastnamefulladdress_0_count','lastnamefulladdress_1_count','lastnamefulladdress_3_count',
                    'lastnamefulladdress_7_count','lastnamefulladdress_14_count','lastnamefulladdress_30_count'
)

summary(alldata)

## combine with days since data
days_since=read.csv("Days_Since.csv")

alldata2=data.table(alldata,days_since[,15:28])

write.csv(alldata,file = "alldata.csv")
