HOUSE_STATUS = ('待出租', '已预约', '已签约')
REPAIR_TYPES = ('水电', '门锁', '管道', '家电', '其他')
USER_ROLES = ('房东', '租客', '物业人员')

# 快递代收状态
PACKAGE_STATUS_REGISTERED = '待入库'   # 租客已登记，等待物业按楼栋收件
PACKAGE_STATUS_STORED = '待取件'       # 物业已入库并生成取件凭证
PACKAGE_STATUS_PICKED = '已取件'       # 凭证核验通过，已完成取件
PACKAGE_STATUS = (
    PACKAGE_STATUS_REGISTERED,
    PACKAGE_STATUS_STORED,
    PACKAGE_STATUS_PICKED,
)

# 前端查询状态用的英文别名 -> 中文状态
PACKAGE_STATE_MAP = {
    'registered': PACKAGE_STATUS_REGISTERED,
    'stored': PACKAGE_STATUS_STORED,
    'picked': PACKAGE_STATUS_PICKED,
}
