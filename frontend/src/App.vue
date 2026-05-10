<template>
  <router-view />
</template>

<style>
/* ── Reset ── */
*, *::before, *::after { box-sizing: border-box; }

/* ── Design tokens ── */
:root {
  --primary:        #409EFF;
  --primary-dark:   #337ecc;
  --primary-light:  #ecf5ff;
  --success:        #10b981;
  --warning:        #f59e0b;
  --danger:         #ef4444;

  --text-1:  #0f172a;
  --text-2:  #475569;
  --text-3:  #94a3b8;
  --border:  #e2e8f0;
  --bg:      #f0f2f5;
  --card:    #ffffff;

  --r-card:       10px;
  --shadow-sm:    0 1px 2px rgba(0,0,0,0.06);
  --shadow-card:  0 1px 4px rgba(0,0,0,0.08), 0 0 0 1px rgba(0,0,0,0.04);
  --shadow-md:    0 4px 12px rgba(0,0,0,0.1);
}

body {
  margin: 0;
  background: var(--bg);
  color: var(--text-1);
  font-family: -apple-system, BlinkMacSystemFont, 'PingFang SC', 'Microsoft YaHei', sans-serif;
  font-size: 14px;
  -webkit-font-smoothing: antialiased;
}

/* ── Element Plus global overrides ── */

/* Card */
.el-card {
  border-radius: var(--r-card) !important;
  box-shadow: var(--shadow-card) !important;
  border: 1px solid var(--border) !important;
}
.el-card__header {
  padding: 14px 20px !important;
  border-bottom: 1px solid var(--border) !important;
  font-size: 14px !important;
  font-weight: 600 !important;
  color: var(--text-1) !important;
}
.el-card__body {
  padding: 20px !important;
}

/* Table */
.el-table {
  font-size: 13px !important;
  --el-table-border-color: var(--border) !important;
}
.el-table th.el-table__cell {
  background: #f8fafc !important;
  color: var(--text-2) !important;
  font-size: 12px !important;
  font-weight: 600 !important;
  text-transform: uppercase;
  letter-spacing: 0.03em;
  padding: 10px 12px !important;
}
.el-table td.el-table__cell {
  padding: 10px 12px !important;
  color: var(--text-1) !important;
}
.el-table .el-table__row:hover > td.el-table__cell {
  background: #f0f7ff !important;
}

/* Form */
.el-form-item__label {
  font-weight: 500 !important;
  color: var(--text-2) !important;
  font-size: 13px !important;
}
.el-input__wrapper {
  border-radius: 7px !important;
}

/* Button */
.el-button {
  border-radius: 7px !important;
  font-weight: 500 !important;
}

/* Tag */
.el-tag { border-radius: 5px !important; }

/* Alert */
.el-alert { border-radius: var(--r-card) !important; }

/* Pagination */
.el-pagination.is-background .el-pager li.is-active {
  background-color: var(--primary) !important;
}
</style>
