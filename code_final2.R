system.time(1:100)
#Since the coalition unity data is only 8 values, I did not bother importing the data
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


################################################################################################################################

#Plots the number of people that voted for each vote per period, did not bother making a function since its not that long
library(rjson)
library(ggplot2)
library(gridExtra)
json_data <- fromJSON(file="n_votes.json")
participation8<-do.call("rbind", json_data[1])
participation4<-do.call("rbind", json_data[2])
participation5<-do.call("rbind", json_data[3])
participation6<-do.call("rbind", json_data[4])

dfparticipation1<-as.data.frame(t(participation4))
dfparticipation2<-as.data.frame(t(participation5))
dfparticipation3<-as.data.frame(t(participation6))
dfparticipation4<-as.data.frame(t(participation8))

dfparticipation1<-cbind(dfparticipation1,1:nrow(dfparticipation1))
dfparticipation2<-cbind(dfparticipation2,1:nrow(dfparticipation2))
dfparticipation3<-cbind(dfparticipation3,1:nrow(dfparticipation3))
dfparticipation4<-cbind(dfparticipation4,1:nrow(dfparticipation4))

colnames(dfparticipation1)[1]<-"ParticipantCount"
colnames(dfparticipation1)[2]<-"NthVote"
colnames(dfparticipation2)[1]<-"ParticipantCount"
colnames(dfparticipation2)[2]<-"NthVote"
colnames(dfparticipation3)[1]<-"ParticipantCount"
colnames(dfparticipation3)[2]<-"NthVote"
colnames(dfparticipation4)[1]<-"ParticipantCount"
colnames(dfparticipation4)[2]<-"NthVote"

source("http://peterhaschke.com/Code/multiplot.R")

plotpart1<-ggplot(data=dfparticipation1, aes(x=NthVote, y=ParticipantCount,))+geom_line(colour="pink")+ggtitle("Period 4")
plotpart2<-ggplot(data=dfparticipation2, aes(x=NthVote, y=ParticipantCount,))+geom_line(colour="orange")+ggtitle("Period 5")
plotpart3<-ggplot(data=dfparticipation3, aes(x=NthVote, y=ParticipantCount,))+geom_line(colour="blue")+ggtitle("Period 6")
plotpart4<-ggplot(data=dfparticipation4, aes(x=NthVote, y=ParticipantCount,))+geom_line(colour="purple")+ggtitle("Period 8")



grid.arrange(arrangeGrob(plotpart1,plotpart2,plotpart3,plotpart4, ncol=2, nrow=2), main=textGrob("Nth Vote Count",gp=gpar(fontsize=20,font=3)))
ggsave(file="PlotNthVoteParticipation.png")


##################################################################################################################


# Creates and then calls a function that will plot participation frequency for each representative
plotparticipation<-function(periodnum){
library("rjson")
library(gridExtra)
library(ggplot2)
filename = c("vote_participation_",periodnum,".json")
json_data <- fromJSON(file=paste(filename,collapse=''))
full<-do.call("rbind", json_data)
df <- data.frame(matrix(unlist(json_data), nrow=length(json_data), byrow=T))

#Unlist data
unlistfull<-matrix(, nrow = length(json_data), ncol=4)
for(i in 1:4){
    col = unlist(full[,i])
    unlistfull[,i]<-col
}
unlistdf<-as.data.frame(unlistfull)
colnames(unlistdf)[2]<-"ParticipationFrequency"
colnames(unlistdf)[1]<-"Party"

#Convert from factor to numeric data type
unlistdf$ParticipationFrequency<-as.numeric(levels(unlistdf$ParticipationFrequency))[unlistdf$ParticipationFrequency]
#unlistdf$ParticipationFrequency<-format(round(unlistdf$ParticipationFrequency*100, 0), nsmall = 0)
unlistdf<-unlistdf[order(unlistdf[,"Party"]),]
unlistdf$Representative<-1:nrow(unlistdf)
rplot<-ggplot(data=unlistdf, aes(x=Representative, y=ParticipationFrequency,fill=Party)) + geom_bar(stat="identity", position=position_dodge())+ggtitle(paste("Period",periodnum))+theme(plot.title=element_text(face="bold", size=20))
return (rplot)
}

plot4<-plotparticipation('4')
plot5<-plotparticipation('5')
plot6<-plotparticipation('6')
plot8<-plotparticipation('8')
source("http://peterhaschke.com/Code/multiplot.R")

#png(filename="PlotRepresentativeParticipationFrequency.png")
#multiplot(plot4,plot5,plot6,plot8,ncol=2)
#dev.off()
grid.arrange(arrangeGrob(plot4,plot5,plot6,plot8, ncol=2, nrow=2), main=textGrob("Representative Participation Frequency",gp=gpar(fontsize=20,font=3)))
ggsave(file="PlotRepresentativeParticipationFrequency.png")


###############################################################################################################################

#Creates and then calls a function which will cluster and then plot representatives based off their vote history
plotclustercoalition<-function(periodnum){
library("rjson")
library(cluster)
library(ggplot2)
filename = c("loyalty_index_coalition_",periodnum,".json")
json_data <- fromJSON(file=paste(filename,collapse=''))
full<-do.call("rbind", json_data)

df <- data.frame(matrix(unlist(json_data), nrow=length(json_data), byrow=T))
#Find columns that will be excluded from clustering
exclude<-which(colnames(full) %in% c("party","loyalty_basic","loyalty_intermediate","loyalty_advanced","score","k","num_votes","firstname","lastname1","lastname2"))
colnum = length(unlist(json_data[1]))
#Unlist the values and fill a matrix with them
unlistfull<-matrix(, nrow = length(json_data), ncol=colnum)
for(i in 1:colnum){
    col = unlist(full[,i])
    unlistfull[,i]<-col
}
colnames(unlistfull)<-colnames(full)
unlistdf<-as.data.frame(unlistfull)

#Cluster using clara package
clara2<-clara(unlistdf[,-exclude],2)
unlistdf$clustering<-clara2$clustering
unlistdf$loyalty_basic<-as.numeric(levels(unlistdf$loyalty_basic))[unlistdf$loyalty_basic]
unlistdfordered <- unlistdf[order(unlistdf$party),]
unlistdfordered$Representative<-1:length(json_data)

#Plot each representative based on loyalty and colored and shaped by cluster and party
rplot<-ggplot(data=unlistdfordered, aes(x=Representative, y=loyalty_basic,color=factor(clustering))) + geom_point(aes(size=15,shape=factor(coalition))) + scale_y_continuous(name="Loyalty")+ theme(legend.title=element_blank(),plot.title=element_text(face="bold", size=15))+ggtitle(paste("Comparing Loyalty Index, Coalition, and Clusters Period",periodnum))
return (rplot)
}

plot4<-plotclustercoalition('4')
plot4
ggsave(file="PlotClusterCoalition4.png")
plot5<-plotclustercoalition('5')
plot5
ggsave(file="PlotClusterCoalition5.png")
plot6<-plotclustercoalition('6')
plot6
ggsave(file="PlotClusterCoalition6.png")
plot8<-plotclustercoalition('8')
plot8
ggsave(file="PlotClusterCoalition8.png")





########################################################################################################


#Creates and then calls a function which will cluster and then plot representatives based off their vote history
plotclusterparty<-function(periodnum){
library("rjson")
library(cluster)
library(ggplot2)
filename = c("loyalty_index_party_",periodnum,".json")
json_data <- fromJSON(file=paste(filename,collapse=''))
full<-do.call("rbind", json_data)

df <- data.frame(matrix(unlist(json_data), nrow=length(json_data), byrow=T))
#Find columns that will be excluded from clustering
exclude<-which(colnames(full) %in% c("party","loyalty_basic","loyalty_intermediate","loyalty_advanced","score","k","num_votes","firstname","lastname1","lastname2"))

colnum = length(unlist(json_data[1]))
unlistfull<-matrix(, nrow = length(json_data), ncol=colnum)
for(i in 1:colnum){
    col = unlist(full[,i])
    unlistfull[,i]<-col
}
colnames(unlistfull)<-colnames(full)

unlistdf<-as.data.frame(unlistfull)
#Cluster using clara package
clara5<-clara(unlistdf[,-exclude],5)

unlistdf$clustering<-clara5$clustering
unlistdf$loyalty_basic<-as.numeric(levels(unlistdf$loyalty_basic))[unlistdf$loyalty_basic]

unlistdfordered <- unlistdf[order(unlistdf$party),]
unlistdfordered$Representative<-1:length(json_data)

rplot<-ggplot(data=unlistdfordered, aes(x=Representative, y=loyalty_basic,color=factor(clustering))) + geom_point(aes(size=15,shape=factor(party))) + scale_y_continuous(name="Loyalty")+ theme(legend.title=element_blank(),plot.title=element_text(face="bold", size=15))+ggtitle(paste("Comparing Loyalty Index, Party, and Clusters Period",periodnum))
return (rplot)
}
plot4<-plotclusterparty('4')
plot4
ggsave(file="PlotCluster4Party.png")
plot5<-plotclusterparty('5')
plot5
ggsave(file="PlotCluster5Party.png")
plot6<-plotclusterparty('6')
plot6
ggsave(file="PlotCluster6Party.png")
plot8<-plotclusterparty('8')
plot8
ggsave(file="PlotCluster8Party.png")


##################################################################################################################

