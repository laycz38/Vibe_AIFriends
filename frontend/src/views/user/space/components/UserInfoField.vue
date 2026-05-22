<script setup>
defineProps({
  userProfile: {
    type: Object,
    default: null,
  },
})
</script>

<template>
  <div v-if="userProfile" class="flex justify-center mt-8 gap-8">
    <div class="avatar">
      <div class="w-32 rounded-full">
        <img
          v-if="userProfile.photo"
          :src="userProfile.photo"
          :alt="userProfile.username"
        />
        <div
          v-else
          class="flex h-full w-full items-center justify-center bg-neutral text-neutral-content text-4xl font-bold"
        >
          {{ (userProfile.username || '?').slice(0, 1).toUpperCase() }}
        </div>
      </div>
    </div>

    <div class="flex flex-col justify-center max-w-md">
      <h2 class="text-2xl font-bold line-clamp-1 break-all">{{ userProfile.username }}</h2>
      <p class="text-sm text-base-content/50 mt-1">
        AIFriends号：{{ userProfile.id }}
      </p>
      <p class="text-sm text-base-content/70 mt-2 line-clamp-3 break-all">
        {{ userProfile.bio?.trim() || '这个人很懒，什么都没写' }}
      </p>
      <div class="flex gap-6 mt-3 text-sm text-base-content/50">
        <span>{{ userProfile.note_count || 0 }} 篇面经</span>
        <span>{{ userProfile.comment_count || 0 }} 条评论</span>
        <span>{{ userProfile.like_count || 0 }} 次点赞</span>
      </div>
    </div>
  </div>
</template>
