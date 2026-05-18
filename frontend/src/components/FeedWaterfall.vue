<script setup>
import NoteCard from './NoteCard.vue'
import { notes } from '../data/notes.js'
</script>

<template>
  <div class="columns-2 md:columns-3 lg:columns-4 xl:columns-5 gap-4 p-4">
    <div
      v-for="note in notes"
      :key="note.id"
      class="break-inside-avoid mb-4"
    >
      <NoteCard :note="note" />
    </div>
  </div>
</template>
