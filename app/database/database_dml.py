####################################################################################
#
#                            SELECT STATEMENTS
#
####################################################################################

######################################
# SELECT ALL COMICS
######################################

allPurchasedComics = \
    "SELECT PC.*, C.*, I.pathExtension as thumbnailExtension " \
    "FROM PurchasedComics PC " \
    "INNER JOIN Comics C " \
    "ON C.id = PC.comicId " \
    "INNER JOIN Images I " \
    "ON C.thumbnail = I.path;"

# Get Comic, its thumbnail path, and series details
singleComicDetail = \
    "SELECT Comics.*, Images.pathExtension AS thumbnailExtension, Series.* " \
    "FROM Comics " \
    "LEFT JOIN Images " \
    "ON Comics.thumbnail = Images.path " \
    "LEFT JOIN Series " \
    "ON Series.id = Comics.seriesId " \
    "WHERE Comics.id=%s;"

singleComicUrls = "SELECT " \
                  "(SELECT ChUL.url " \
                  "FROM Comics_has_URLs ChUL " \
                  "LEFT OUTER JOIN URLs UL " \
                  "ON ChUL.url = UL.url " \
                  "WHERE ChUL.comicId = C.id AND UL.type = 'purchase') as purchaseURL, " \
                  "(SELECT ChUL.url " \
                  "FROM Comics_has_URLs ChUL " \
                  "LEFT OUTER JOIN URLs UL " \
                  "ON ChUL.url = UL.url " \
                  "WHERE ChUL.comicId = C.id AND UL.type = 'detail') as detailURL, " \
                  "(SELECT ChUL.url " \
                  "FROM Comics_has_URLs ChUL " \
                  "LEFT OUTER JOIN URLs UL " \
                  "ON ChUL.url = UL.url " \
                  "WHERE ChUL.comicId = C.id AND UL.type = 'comiclink') as comicLink, " \
                  "(SELECT ChUL.url " \
                  "FROM Comics_has_URLs ChUL " \
                  "LEFT OUTER JOIN URLs UL " \
                  "ON ChUL.url = UL.url " \
                  "WHERE ChUL.comicId = C.id AND UL.type = 'reader') as readerURL, " \
                  "(SELECT ChUL.url " \
                  "FROM Comics_has_URLs ChUL " \
                  "LEFT OUTER JOIN URLs UL " \
                  "ON ChUL.url = UL.url " \
                  "WHERE ChUL.comicId = C.id AND UL.type = 'inAppLink') as inAppLink, " \
                  "(SELECT ChUL.url " \
                  "FROM Comics_has_URLs ChUL " \
                  "LEFT OUTER JOIN URLs UL " \
                  "ON ChUL.url = UL.url " \
                  "WHERE ChUL.comicId = C.id AND UL.type = 'inAppLink') as inAppLink " \
                  "FROM Comics C " \
                  "WHERE C.id=%s;"

singleComicSeries = "SELECT * FROM "
