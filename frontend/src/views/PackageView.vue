<template>
  <main class="page">
    <section class="toolbar">
      <div>
        <h1>快递代收与取件</h1>
        <p>租客登记预计到达快递，物业按楼栋收件入库并生成取件凭证，取件时核对凭证后推进状态。</p>
      </div>
      <el-button :loading="loading" @click="loadList">刷新记录</el-button>
    </section>

    <section class="action-grid">
      <el-card shadow="never">
        <template #header><strong>① 租客登记快递</strong></template>
        <el-form label-position="top" :model="regForm" @submit.prevent>
          <el-form-item label="快递单号" required>
            <el-input v-model="regForm.trackingNo" placeholder="如 SF100245" clearable />
          </el-form-item>
          <el-form-item label="快递公司">
            <el-input v-model="regForm.company" placeholder="顺丰 / 京东 / 中通…" clearable />
          </el-form-item>
          <el-form-item label="租客姓名" required>
            <el-input v-model="regForm.tenantName" clearable />
          </el-form-item>
          <el-form-item label="手机号" required>
            <el-input v-model="regForm.tenantPhone" clearable />
          </el-form-item>
          <el-form-item label="楼栋">
            <el-input v-model="regForm.building" placeholder="如 3 栋" clearable />
          </el-form-item>
          <el-form-item label="房号">
            <el-input v-model="regForm.roomNo" placeholder="如 501" clearable />
          </el-form-item>
          <el-button type="primary" class="full" :loading="submitting === 'reg'" @click="submitRegister">提交登记</el-button>
        </el-form>
      </el-card>

      <el-card shadow="never">
        <template #header><strong>② 物业收件入库</strong></template>
        <el-form label-position="top" :model="storeForm" @submit.prevent>
          <el-form-item label="快递单号" required>
            <el-input v-model="storeForm.trackingNo" placeholder="按单号查找已登记快递" clearable />
          </el-form-item>
          <el-form-item label="入住院栋" required>
            <el-input v-model="storeForm.building" placeholder="按楼栋收件，如 3 栋" clearable />
          </el-form-item>
          <el-form-item label="房号">
            <el-input v-model="storeForm.roomNo" clearable />
          </el-form-item>
          <el-form-item label="经办人">
            <el-input v-model="storeForm.operator" placeholder="物业人员姓名" clearable />
          </el-form-item>
          <el-alert type="info" :closable="false" class="tip" title="入库后系统自动生成 6 位取件凭证" />
          <el-button type="warning" class="full" :loading="submitting === 'store'" @click="submitStore">确认入库</el-button>
        </el-form>
      </el-card>

      <el-card shadow="never">
        <template #header><strong>③ 核对凭证取件</strong></template>
        <el-form label-position="top" :model="pickupForm" @submit.prevent>
          <el-form-item label="快递单号" required>
            <el-input v-model="pickupForm.trackingNo" clearable />
          </el-form-item>
          <el-form-item label="取件凭证" required>
            <el-input v-model="pickupForm.pickupCode" placeholder="通知中 6 位数字凭证" maxlength="16" clearable />
          </el-form-item>
          <el-alert type="info" :closable="false" class="tip" title="凭证与单号必须同时匹配方可取件" />
          <el-button type="success" class="full" :loading="submitting === 'pickup'" @click="submitPickup">核验并取件</el-button>
        </el-form>
      </el-card>
    </section>

    <section class="records">
      <div class="records-head">
        <h2>快递记录</h2>
        <el-radio-group v-model="activeState" @change="loadList">
          <el-radio-button label="pending">待取件</el-radio-button>
          <el-radio-button label="registered">待入库</el-radio-button>
          <el-radio-button label="picked">已取件</el-radio-button>
          <el-radio-button label="">全部</el-radio-button>
        </el-radio-group>
      </div>

      <el-table v-loading="loading" :data="records" empty-text="暂无记录" border stripe>
        <el-table-column prop="trackingNo" label="快递单号" min-width="130" />
        <el-table-column prop="company" label="公司" min-width="80" />
        <el-table-column label="租客" min-width="110">
          <template #default="{ row }">{{ row.tenantName }} {{ row.tenantPhone }}</template>
        </el-table-column>
        <el-table-column label="楼栋/房号" min-width="100">
          <template #default="{ row }">{{ [row.building, row.roomNo].filter(Boolean).join(' ') || '-' }}</template>
        </el-table-column>
        <el-table-column label="状态" min-width="90">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="取件凭证" min-width="100">
          <template #default="{ row }">
            <span v-if="row.pickupCode" class="code">{{ row.pickupCode }}</span>
            <span v-else class="muted">-</span>
          </template>
        </el-table-column>
        <el-table-column prop="registeredAt" label="登记时间" min-width="130" />
        <el-table-column prop="storedAt" label="入库时间" min-width="130">
          <template #default="{ row }">{{ row.storedAt || '-' }}</template>
        </el-table-column>
        <el-table-column prop="pickedAt" label="取件时间" min-width="130">
          <template #default="{ row }">{{ row.pickedAt || '-' }}</template>
        </el-table-column>
      </el-table>
    </section>
  </main>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue';
import { ElMessage } from 'element-plus';
import { getPackages, pickupPackage, registerPackage, storePackage, type PackageState } from '../api/packages';
import type { PackageRecord, PackageStatus } from '../types/domain';

const records = ref<PackageRecord[]>([]);
const loading = ref(false);
const activeState = ref<PackageState>('pending');
const submitting = ref<'' | 'reg' | 'store' | 'pickup'>('');

const regForm = reactive({ trackingNo: '', company: '', tenantName: '', tenantPhone: '', building: '', roomNo: '' });
const storeForm = reactive({ trackingNo: '', building: '', roomNo: '', operator: '' });
const pickupForm = reactive({ trackingNo: '', pickupCode: '' });

async function loadList() {
  loading.value = true;
  try {
    records.value = await getPackages(activeState.value);
  } catch (error) {
    ElMessage.error((error as Error).message);
  } finally {
    loading.value = false;
  }
}

function requireFields(form: Record<string, string>, keys: string[]): boolean {
  return keys.every((key) => (form[key] ?? '').trim() !== '');
}

async function submitRegister() {
  if (!requireFields(regForm as unknown as Record<string, string>, ['trackingNo', 'tenantName', 'tenantPhone'])) {
    ElMessage.warning('请填写快递单号、租客姓名和手机号');
    return;
  }
  submitting.value = 'reg';
  try {
    await registerPackage({ ...regForm });
    ElMessage.success('快递登记成功，等待物业入库');
    Object.assign(regForm, { trackingNo: '', company: '', tenantName: '', tenantPhone: '', building: '', roomNo: '' });
    await loadList();
  } catch (error) {
    ElMessage.error((error as Error).message);
  } finally {
    submitting.value = '';
  }
}

async function submitStore() {
  if (!requireFields(storeForm as unknown as Record<string, string>, ['trackingNo', 'building'])) {
    ElMessage.warning('请填写快递单号和入住院栋');
    return;
  }
  submitting.value = 'store';
  try {
    const result = await storePackage(storeForm.trackingNo, storeForm.building, storeForm.roomNo, storeForm.operator);
    ElMessage.success(`入库成功，取件凭证：${result.pickupCode}`);
    Object.assign(storeForm, { trackingNo: '', building: '', roomNo: '', operator: '' });
    await loadList();
  } catch (error) {
    ElMessage.error((error as Error).message);
  } finally {
    submitting.value = '';
  }
}

async function submitPickup() {
  if (!requireFields(pickupForm as unknown as Record<string, string>, ['trackingNo', 'pickupCode'])) {
    ElMessage.warning('请填写快递单号和取件凭证');
    return;
  }
  submitting.value = 'pickup';
  try {
    await pickupPackage(pickupForm.trackingNo, pickupForm.pickupCode);
    ElMessage.success('核验通过，取件成功');
    pickupForm.trackingNo = '';
    pickupForm.pickupCode = '';
    await loadList();
  } catch (error) {
    ElMessage.error((error as Error).message);
  } finally {
    submitting.value = '';
  }
}

function statusType(status: PackageStatus): 'info' | 'warning' | 'success' {
  if (status === '待取件') return 'warning';
  if (status === '已取件') return 'success';
  return 'info';
}

onMounted(loadList);
</script>
