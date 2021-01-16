const showResults = () => {
    // read input data
    let mData = {}
    mData["regid"] = $("#regid").val();
    mData["level"] = $("#level input:checked").val();
    mData["who"]   = $("#who input:checked").val();

    console.log(mData);
}
