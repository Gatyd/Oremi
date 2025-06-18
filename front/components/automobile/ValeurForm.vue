<template>
    <div>
        <UForm :state="state" @submit="$emit('submit', $event)">
            <div class="grid grid-cols-4">
                <div class="col-span-3">
                    <!-- Valeur d'achat du véhicule -->
                    <div class="mb-6">
                        <label class="block font-medium text-gray-700 mb-2">
                            Valeur d'achat du véhicule
                        </label>
                        <div class="relative">
                            <CustomInput v-model="formattedValeurAchat" class="w-full pr-16" placeholder="200000000"
                                @update:model-value="calculateValeurVenale" />
                            <div
                                class="absolute right-3 top-1/2 transform -translate-y-1/2 bg-[#0066A0] text-white px-3 py-1 rounded text-sm font-medium">
                                FCFA
                            </div>
                        </div>
                    </div>

                    <!-- Valeur vénale (calculée automatiquement) -->
                    <div class="mb-6">
                        <label class="block font-medium text-gray-700 mb-2">
                            Valeur vénale
                        </label>
                        <div class="relative">
                            <CustomInput v-model="formattedValeurVenale" class="w-full pr-16" />
                            <div
                                class="absolute right-3 top-1/2 transform -translate-y-1/2 bg-[#0066A0] text-white px-3 py-1 rounded text-sm font-medium">
                                FCFA
                            </div>
                        </div>
                        <p class="text-xs text-gray-500 mt-1">
                            Calculée automatiquement selon l'âge du véhicule (-10% par an)
                        </p>
                    </div>

                    <!-- Zone de résidence -->
                    <div class="mb-8">
                        <label class="block font-medium text-gray-700 mb-2">
                            Zone de résidence
                        </label>
                        <CustomSelect v-model="state.zone_residence" class="w-full" :items="zones"
                            placeholder="ZOGBODOMEY">
                            <template #trailing>
                                <Icon name="heroicons:chevron-down" class="w-4 h-4" />
                            </template>
                        </CustomSelect>
                    </div>
                </div>
            </div>
        </UForm>
    </div>
</template>

<script setup lang="ts">
// Props
interface Props {
    vehicleData?: {
        date_mise_circulation: string
        marque: string
        modele: string
    }
}

const state = reactive({
    valeur_achat: 0,
    valeur_venale: 0,
    zone_residence: ''
})
const props = defineProps<Props>()

// Events
defineEmits<{
    submit: [event: any]
}>()

// Options pour les zones de résidence
const zones = [
    'PARIS',
    'PROVINCE',
    'DOM-TOM',
    'ETRANGER'
]

// Calculer automatiquement la valeur vénale
const calculateValeurVenale = () => {
    if (!state.valeur_achat || !props.vehicleData?.date_mise_circulation) {
        return
    }

    const dateMiseCirculation = new Date(props.vehicleData.date_mise_circulation)
    const currentDate = new Date()

    // Calculer la différence en années (avec les mois)
    const diffTime = currentDate.getTime() - dateMiseCirculation.getTime()
    const diffYears = Math.floor(diffTime / (1000 * 60 * 60 * 24 * 365.25))

    // Dépréciation linéaire : 10% de la valeur initiale par an
    // Formule : Valeur vénale = Valeur d'achat - (Valeur d'achat × 0.10 × nombre d'années)
    // const depreciationPercentage = Math.min(diffYears * 0.10, 0.90) // Maximum 90% de dépréciation
    const valeurVenale = Math.max(0, state.valeur_achat - (state.valeur_achat * 0.10 * diffYears))
    console.log('Valeur vénale calculée:', valeurVenale)

    state.valeur_venale = Math.round(valeurVenale)
}

// Watcher pour recalculer automatiquement la valeur vénale
watch(() => state.valeur_achat, calculateValeurVenale)
watch(() => props.vehicleData?.date_mise_circulation, calculateValeurVenale)

// Formater les nombres avec espaces
const formatNumber = (value: number) => {
    return value.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ' ')
}

// Parser les nombres depuis l'input formaté
const parseFormattedNumber = (value: string) => {
    return parseInt(value.replace(/\s/g, '')) || 0
}

// Computed pour les valeurs formatées
const formattedValeurAchat = computed({
    get: () => state.valeur_achat ? formatNumber(state.valeur_achat) : '',
    set: (value: string) => {
        state.valeur_achat = parseFormattedNumber(value)
    }
})

const formattedValeurVenale = computed(() => {
    return state.valeur_venale ? formatNumber(state.valeur_venale) : ''
})
</script>
