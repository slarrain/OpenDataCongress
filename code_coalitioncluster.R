# Creates and then calls a function which will cluster and then plot representatives based off their vote history
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