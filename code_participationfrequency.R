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
