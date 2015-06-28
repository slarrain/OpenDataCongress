system.time(1:100)
# Since the coalition unity data is only 8 values, I did not bother importing the data
Coalition<-c('Concertacion','Alianza')
Period<-c('4','5','6')
Percentage<-c(58.7,45.6,53.7,59.3,44.0,72.6,73.5,70.3)
data.frame(Coalition,Percentage)
Period<-c('4','4','5','5','6','6','8','8')
CoalitionUnity<-data.frame(Period,Coalition,Percentage)

library(ggplot2)
CoalitionUnity<-rbind(CoalitionUnity,c('8','Concertacion',73.5))
CoalitionUnity<-data.frame(Period,Coalition,Percentage)
ggplot(data=CoalitionUnity, aes(x=Coalition, y=Percentage, fill=Period)) + geom_bar(stat="identity", position=position_dodge())+ geom_text(aes(y=Percentage, ymax=Percentage, label=Percentage),position= position_dodge(width=0.9), vjust=-.5)+ggtitle("Coalition Unity Votes")+theme(plot.title=element_text(face="bold", size=20))
ggsave(file="PlotCoalitionUnity.png")
library(rjson)
json_data_partyunity <- fromJSON(file="party_unity_vote.json")
partyunity<-do.call("rbind", json_data_partyunity)
library(ggplot2)
partyunity<-as.data.frame(t(partyunity))
partyunity<-sapply(partyunity,unlist)

#Find percentage of total which is the final row
matrixpartyunity<-as.matrix(partyunity)
matrixpartyunity<-t(t(matrixpartyunity)/matrixpartyunity[6,])
partyunity<-as.data.frame(matrixpartyunity)
partyunity<-partyunity[-6,]
colnames(partyunity)<-c("P8","P4","P5","P6")

library(reshape)
partyunity<-cbind(rownames(partyunity),melt(partyunity))
colnames(partyunity)[1]<-"Party"
partyunity$value<-format(round(partyunity$value*100, 0), nsmall = 0)
colnames(partyunity)[3]<-"Percentage"
#Reorder factor levels
partyunity$Party<-factor(partyunity$Party,levels(partyunity$Party)[c(3,2,1,4,5)])
partyunity$period<-factor(partyunity$variable,levels(partyunity$variable)[c(2,3,4,1)])
partyunity$period
partyunity$variable<-NULL

ggplot(data=partyunity, aes(x=Party, y=Percentage)) + geom_bar(aes(fill=period),stat="identity", position=position_dodge())+ ggtitle("Party Unity Votes")+theme(plot.title=element_text(face="bold", size=20))
ggsave(file="PlotPartyUnity.png")