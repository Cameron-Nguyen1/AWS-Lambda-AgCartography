test_runtime <- function(Records){
  set.seed(8675309)
  dep = c("rjson","ggplot2","stringr","reshape2","paletteer","Racmacs","aws.s3")
  hex_to_raw <- function(hex) { sapply(seq(1, nchar(hex), by = 2), function(x) as.raw(as.hexmode(substr(hex, x, x + 1)))) }
  lapply(dep,library,character.only=TRUE)
  setwd("/tmp")
  key_in = Records$s3$object$key
  jsonfile = get_object(key_in,bucket = "YOURINPUTBUCKET") #REPLACE
  jsonfile = paste0(jsonfile,collapse = "")
  raw_bytes = hex_to_raw(jsonfile)
  chars = rawToChar(raw_bytes)
  print(chars)
  json_data = fromJSON(chars)
  print("read jsonfile")

  dir.create(json_data$out)
  lines = strsplit(json_data$input, "\n")[[1]]
  column_names = unlist(strsplit(lines[1], ","))
  data = lapply(lines[2:length(lines)], function(line) unlist(strsplit(line, ",")))
  y = as.data.frame(do.call(rbind, data), stringsAsFactors = FALSE)
  colnames(y) = column_names
  nantigen = ncol(y)-1
  nsera = nrow(y)
  rownames(y) = paste0("S_",y[,1])
  y = y[,-1]
  y[1:nantigen] = lapply(y[1:nantigen],as.numeric)
  y = t(y)

  x_log2 = log2(y/10)

  #Caluclate Distance Table using Log Titer Table
  vec = list()
  for (i in 1:ncol(x_log2)){
      vec = append(vec, max(x_log2[,i]))
  }
  for (i in 1:length(vec)){
    x_log2[,i] = vec[[i]]  - x_log2[,i]
  }
  a = paste0(getwd(),"/",json_data$out,"/",json_data$prefix,"_Cart_Distance_between_groups.csv")
  a = as.character(a)
  write.csv(x_log2, a)

  #Create Antigenic Map
  map = acmap(titer_table = y)
  agNames(map) = row.names(x_log2)
  agGroups(map) = row.names(x_log2)
  dilutionStepsize(map) = 2
  map = optimizeMap(map = map, number_of_dimensions=2, number_of_optimizations=1000, minimum_column_basis="none")
  saveRDS(map,paste0(getwd(),"/",json_data$out,"/",json_data$prefix,"_mapobj.rds"))

  #Save coords to calculate distance of Antigen-Antigen and Sera-Sera
  save.coords(map, paste0(json_data$out,"/",json_data$prefix,"_Cart_racmacs_coordinates.csv"))

  #Read coord data to calculate within-group distances!
  df1 = read.csv(paste0(json_data$out,"/",json_data$prefix,"_Cart_racmacs_coordinates.csv"))
  if (toupper(json_data$agSort) == "TRUE"){
    df1[1:nantigen,] = df1[1:nantigen,][order(df1[1:nantigen,]$name),]
  }
  df2 = df1[str_detect(df1$type, "antigen"),] #ANTIGEN DISTANCES
  df2 = subset(df2, select = -c(1))
  rownames(df2) = df2[,1]
  df2 = subset(df2, select = -c(1))
  AgDistances = reshape2::melt(as.matrix(dist(df2))) #Distance Matrix command
  colnames(AgDistances) = c("Virus 1","Virus 2","Distance")
  write.csv(AgDistances,paste0(json_data$out,"/",json_data$prefix,"_Cart_Distance_within_ag.csv"))

  df3 = df1[str_detect(df1$type, "sera"),] #SERA DISTANCES
  rownames(df3) = df3$name
  df3 = df3[,c(-1,-2)]
  SeraDistances = reshape2::melt(as.matrix(dist(df3)))
  colnames(SeraDistances)=c("Sera 1", "Sera 2", "Distance")
  write.csv(SeraDistances,paste0(json_data$out,"/",json_data$prefix,"_Cart_Distance_within_sera.csv"))

  alpha = str_split_fixed(json_data$opacity, ",", 2) #Alphas

  #Plots'n'stuff
  if (nantigen > 20)
    {
      df1$colors = c(paletteer_d("ggsci::default_igv")[1:nantigen],rep("#0d0101",nsera))
    }else{
      df1$colors = c(paletteer_d("ggsci::category20_d3")[1:nantigen],rep("#0d0101",nsera))}
  size = str_split_fixed(json_data$psizes,",",2) #Sizes
  df1$size= c(rep(as.numeric(size[1]),nantigen),rep(as.numeric(size[2]),nsera))
  df1$Type = c(rep("Antigen",nantigen),rep("Sera",nsera))
  df1$name = c(df1$name[1:nantigen],rep("Sera",nsera))
  df1$alpha = c(rep(as.numeric(alpha[1]),nantigen),rep(as.numeric(alpha[2]),nsera))
  z = str_split_fixed(json_data$xy_lim, ",", 4) #XY_lims
  if (toupper(json_data$agOverprint) == "TRUE"){
      df1 = rbind(df1[grepl("Sera",df1$Type),],df1[grepl("Antigen",df1$Type),])
  }

  mypdf = paste0(getwd(),"/",json_data$out,"/",json_data$prefix,"_",z[2],"x",z[4],".pdf")
  mp =ggplot(df1, aes(x=X,y=X.1)) +
      geom_point(alpha=df1$alpha,size=df1$size,
                aes(shape = Type, color = name)) +
      # form_blobs_2d(blobject=blobject.95,meta=df1) +
      scale_color_manual("Name", values=c(df1[grepl("Antigen",df1$Type),5],"#0d0101"),breaks=df1[grepl("Antigen",df1$Type),2])+
      ylab("Y") +
      coord_fixed(ylim=c(as.numeric(z[1]),as.numeric(z[2])),xlim=c(as.numeric(z[3]),as.numeric(z[4])))+
      scale_x_continuous(breaks=scales::pretty_breaks(n=(as.numeric(z[2])*2)+1))+
      scale_y_continuous(breaks=scales::pretty_breaks(n=(as.numeric(z[4])*2)+1))+
      theme(panel.grid.minor= element_blank(),axis.text.x = element_text(size = 12), axis.text.y = element_text(size = 12), axis.ticks = element_line(size=1.15),
            legend.text = element_text(size = 12), legend.title = element_text(size = 14))
  ggsave(filename=mypdf,plot=mp)
  zip(zipfile=paste0(json_data$out,".zip"),files=json_data$out)
  put_object(file=paste0(json_data$out,".zip"), object=paste0(json_data$out,".zip"), bucket="YOUROUTPUTBUCKET") #REPLACE
  unlink(json_data$out,recursive=TRUE)
  unlink(paste0(json_data$out,".zip"))
}
lambdr::start_lambda()