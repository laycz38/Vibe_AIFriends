<script setup>
import { RouterLink } from 'vue-router'
</script>

<template>
  <div class="navbar bg-base-100 shadow-sm">
    <div class="flex-1">
      <RouterLink to="/" class="btn btn-ghost text-xl">AIFriends</RouterLink>
    </div>
    <div class="flex-none">
      <ul class="menu menu-horizontal px-1">
        <li><RouterLink to="/">首页</RouterLink></li>
        <li><RouterLink to="/about">关于</RouterLink></li>
      </ul>
    </div>
  </div>
</template>
