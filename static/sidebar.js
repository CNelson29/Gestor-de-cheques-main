function toggleSidebar() {
    var sidebar = document.getElementById("sidebar");
    var mainContent = document.getElementById("mainContent");

    sidebar.classList.toggle("sidebar-open");
    mainContent.classList.toggle("content-shift");
}
