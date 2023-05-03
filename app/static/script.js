function isPurchasedChanged() {
    let box_value = document.getElementById("isPurchased").value;
    console.log(box_value)
    if (box_value === 'Yes') {
        document.getElementById("purchaseDate").style.display = "initial"
        document.getElementById("purchasePrice").style.display = "initial"
        document.getElementById("purchaseType").style.display = "initial"
    } else {
        document.getElementById("purchaseDate").style.display = "none"
        document.getElementById("purchasePrice").style.display = "none"
        document.getElementById("purchaseType").style.display = "none"
    }
}


