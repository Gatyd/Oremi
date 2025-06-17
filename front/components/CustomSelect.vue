<template>
    <USelectMenu v-bind="$attrs"
        class="h-12 text-center text-xl rounded-md border-2 font-semibold bg-transparent 
        placeholder:text-gray-300 text-gray-600 focus:border-[#EDF3F7] border-[#EDF3F7]">
        <template #trailing>
            <slot name="trailing"></slot>
        </template>
    </USelectMenu>
</template>