FROM public.ecr.aws/lambda/provided:al2023

ENV R_VER=4.3.1

RUN dnf install -y libcurl-devel openssl-devel vim
RUN mkdir -p /opt
RUN curl -o /opt/R-${R_VER}-1-1.x86_64.rpm https://cdn.posit.co/r/rhel-9/pkgs/R-${R_VER}-1-1.x86_64.rpm
RUN dnf install -y $(rpm -qR /opt/R-${R_VER}-1-1.x86_64.rpm | tr '\n' ' ')
RUN rpm -i /opt/R-${R_VER}-1-1.x86_64.rpm && rm /opt/R-${R_VER}-1-1.x86_64.rpm

ENV PATH="${PATH}:/opt/R/${R_VER}/bin/"
RUN echo 'options(repos = c(PPM = "https://packagemanager.posit.co/cran/__linux__/rhel9/latest"))' >> $HOME/.Rprofile

RUN Rscript -e "install.packages(c('Racmacs','lambdr'),repos='http://cran.us.r-project.org')"
RUN Rscript -e "install.packages('https://cran.r-project.org/src/contrib/Archive/ggplot2/ggplot2_3.4.4.tar.gz', repos=NULL, type='source')"
RUN Rscript -e "install.packages(c('rjson','httr', 'jsonlite', 'logger', 'remotes','stringr','reshape2','paletteer','aws.s3'))"

RUN mkdir -p /lambda
COPY test_runtime.r /lambda
RUN chmod 755 -R /lambda 

WORKDIR /
COPY bootstrap.sh /bootstrap.sh
RUN chmod +x /bootstrap.sh
ENTRYPOINT ["/bootstrap.sh"]

CMD ["test_runtime"]