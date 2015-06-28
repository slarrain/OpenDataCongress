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