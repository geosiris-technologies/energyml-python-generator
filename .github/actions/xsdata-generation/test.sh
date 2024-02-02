
function folder_match_pkg() {
    PKG=$(echo "$1" | tr '[:upper:]' '[:lower:]')
    FOLDER=$(echo "$2" | tr '[:upper:]' '[:lower:]')
    if [ "$PKG" = "$FOLDER" ] || { [ "$PKG" = "common" ] && [ "$FOLDER" = "eml" ] ;};
    then
      return 0;
    else
      return 1;
    fi
}