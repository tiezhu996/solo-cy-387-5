<template>
  <div>
    <nav class="app-nav">
      <span class="brand">RentFind</span>
      <el-radio-group v-model="tab" size="default">
        <el-radio-button label="home">租房与报修</el-radio-button>
        <el-radio-button label="package">快递代收取件</el-radio-button>
      </el-radio-group>
    </nav>
    <HomeView v-if="tab === 'home'" />
    <PackageView v-else />
  </div>
</template>
<script setup lang="ts">
import { ref } from 'vue';
import HomeView from './views/HomeView.vue';
import PackageView from './views/PackageView.vue';

const tab = ref<'home' | 'package'>('package');
</script>
