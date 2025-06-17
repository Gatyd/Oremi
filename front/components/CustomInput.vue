<script setup lang="ts">
const model = defineModel<String | number>({
    default: '',
    required: true
})
</script>
<template>
    <input v-bind="$attrs" v-model="model"
    class="h-12 text-center text-2xl rounded-md border-2 font-semibold placeholder:text-gray-300 text-gray-600 focus:border-[#EDF3F7] border-[#EDF3F7]" /> 
</template>