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
