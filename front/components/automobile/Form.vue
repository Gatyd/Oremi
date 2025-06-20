<script setup lang="ts">
import VehiculeForm from './VehiculeForm.vue'
import ValeurForm from './ValeurForm.vue'

// Props et state du formulaire
const currentStep = ref(1) // Étape actuelle (1 à 4)
const currentStepTitle = ref('Identifier mon véhicule')
const progressWidth = ref('25%') // Pour la première étape

// Mapping des titres par étape
const stepTitles: Record<number, string> = {
    1: 'Identifier mon véhicule',
    2: 'Valeur du véhicule',
    3: 'Informations du bien',
    4: 'Paiement'
}

// Mise à jour du titre selon l'étape
watch(currentStep, (newStep) => {
    currentStepTitle.value = stepTitles[newStep] || 'Identifier mon véhicule'
    progressWidth.value = `${(newStep / 4) * 100}%`
})

// State du formulaire pour toutes les étapes
const formState = reactive({
    // Étape 1: Identification du véhicule
    imatriculationPart1: '',
    imatriculationPart2: '',
    imatriculationPart3: '',
    marque: '',
    modele: '',
    puissance_fiscale: 1,
    numero_chassis: '',
    date_mise_circulation: '',
    places_assises: 5,
    carburation: '',

    // Étape 2: Valeur du véhicule
    valeur_achat: 0,
    valeur_venale: 0,
    zone_residence: '',

    // Autres étapes à ajouter plus tard
    // Étape 3: Informations du bien
    // Étape 4: Paiement
})

// Computed pour séparer les données par étape
const vehicleData = computed(() => ({
    imatriculationPart1: formState.imatriculationPart1,
    imatriculationPart2: formState.imatriculationPart2,
    imatriculationPart3: formState.imatriculationPart3,
    marque: formState.marque,
    modele: formState.modele,
    puissance_fiscale: formState.puissance_fiscale,
    numero_chassis: formState.numero_chassis,
    date_mise_circulation: formState.date_mise_circulation,
    places_assises: formState.places_assises,
    carburation: formState.carburation
}))

const valeurData = computed(() => ({
    valeur_achat: formState.valeur_achat,
    valeur_venale: formState.valeur_venale,
    zone_residence: formState.zone_residence
}))

// Fonction de soumission
const handleSubmit = () => {
    console.log('Formulaire soumis:', formState)
    // Logique de navigation vers l'étape suivante
    if (currentStep.value < 4) {
        currentStep.value++
    }
}
</script>

<template>
    <img src="/form_header.png" class="fixed z-50 top-0 left-0" alt="">
    <div class="max-w-4xl lg:mt-16 pt-10 xl:pt-10 xl:mt-24 mb-20 mx-auto p-6">
        <!-- Titre principal -->
        <h1 class="text-3xl font-bold text-gray-900 mb-8">Devis Automobile</h1>

        <!-- Étapes du processus -->
        <div class="flex items-center justify-center mb-8">
            <img src="/steps.png" class="" alt="">
            <!-- <div class="flex items-center">
                <!-- Étape 1: Devis 
                <div class="flex items-center bg-white rounded-full px-4 py-2 shadow-sm border"
                    :class="{ 'border-[#3C3390]': currentStep === 1, 'border-gray-200': currentStep !== 1 }">
                    <div class="flex items-center">
                        <!-- Icône ou numéro 
                        <div v-if="currentStep > 1"
                            class="w-6 h-6 bg-[#3C3390] rounded-full flex items-center justify-center mr-2">
                            <Icon name="heroicons:check" class="w-4 h-4 text-white" />
                        </div>
                        <div v-else-if="currentStep === 1"
                            class="w-6 h-6 bg-[#3C3390] text-white rounded-full flex items-center justify-center text-xs font-medium mr-2">
                            1
                        </div>
                        <div v-else
                            class="w-6 h-6 bg-gray-300 text-gray-500 rounded-full flex items-center justify-center text-xs font-medium mr-2">
                            1
                        </div>
                        <span class="text-sm font-medium"
                            :class="currentStep >= 1 ? 'text-[#3C3390]' : 'text-gray-500'">Devis</span>
                    </div>
                </div>

                <!-- Séparateur 
                <div class="w-8 h-0.5 mx-2" :class="currentStep > 1 ? 'bg-[#3C3390]' : 'bg-gray-300'"></div>

                <!-- Étape 2: Identification 
                <div class="flex items-center bg-white rounded-full px-4 py-2 shadow-sm border"
                    :class="{ 'border-[#3C3390]': currentStep === 2, 'border-gray-200': currentStep !== 2 }">
                    <div class="flex items-center">
                        <!-- Icône ou numéro 
                        <div v-if="currentStep > 2"
                            class="w-6 h-6 bg-[#3C3390] rounded-full flex items-center justify-center mr-2">
                            <Icon name="heroicons:check" class="w-4 h-4 text-white" />
                        </div>
                        <div v-else-if="currentStep === 2"
                            class="w-6 h-6 bg-[#3C3390] text-white rounded-full flex items-center justify-center text-xs font-medium mr-2">
                            2
                        </div>
                        <div v-else
                            class="w-6 h-6 bg-gray-300 text-gray-500 rounded-full flex items-center justify-center text-xs font-medium mr-2">
                            2
                        </div>                        <span class="text-sm font-medium"
                            :class="currentStep >= 2 ? 'text-[#3C3390]' : 'text-gray-500'">Valeur</span>
                    </div>
                </div>

                <!-- Séparateur 
                <div class="w-8 h-0.5 mx-2" :class="currentStep > 2 ? 'bg-[#3C3390]' : 'bg-gray-300'"></div>

                <!-- Étape 3: Informations du bien 
                <div class="flex items-center bg-white rounded-full px-4 py-2 shadow-sm border"
                    :class="{ 'border-[#3C3390]': currentStep === 3, 'border-gray-200': currentStep !== 3 }">
                    <div class="flex items-center">
                        <!-- Icône ou numéro 
                        <div v-if="currentStep > 3"
                            class="w-6 h-6 bg-[#3C3390] rounded-full flex items-center justify-center mr-2">
                            <Icon name="heroicons:check" class="w-4 h-4 text-white" />
                        </div>
                        <div v-else-if="currentStep === 3"
                            class="w-6 h-6 bg-[#3C3390] text-white rounded-full flex items-center justify-center text-xs font-medium mr-2">
                            3
                        </div>
                        <div v-else
                            class="w-6 h-6 bg-gray-300 text-gray-500 rounded-full flex items-center justify-center text-xs font-medium mr-2">
                            3
                        </div>
                        <span class="text-sm font-medium"
                            :class="currentStep >= 3 ? 'text-[#3C3390]' : 'text-gray-500'">Informations du bien</span>
                    </div>
                </div>

                <!-- Séparateur 
                <div class="w-8 h-0.5 mx-2" :class="currentStep > 3 ? 'bg-[#3C3390]' : 'bg-gray-300'"></div>

                <!-- Étape 4: Paiement 
                <div class="flex items-center bg-white rounded-full px-4 py-2 shadow-sm border"
                    :class="{ 'border-[#3C3390]': currentStep === 4, 'border-gray-200': currentStep !== 4 }">
                    <div class="flex items-center">
                        <!-- Icône ou numéro 
                        <div v-if="currentStep > 4"
                            class="w-6 h-6 bg-[#3C3390] rounded-full flex items-center justify-center mr-2">
                            <Icon name="heroicons:check" class="w-4 h-4 text-white" />
                        </div>
                        <div v-else-if="currentStep === 4"
                            class="w-6 h-6 bg-[#3C3390] text-white rounded-full flex items-center justify-center text-xs font-medium mr-2">
                            4
                        </div>
                        <div v-else
                            class="w-6 h-6 bg-gray-300 text-gray-500 rounded-full flex items-center justify-center text-xs font-medium mr-2">
                            4
                        </div>
                        <span class="text-sm font-medium"
                            :class="currentStep >= 4 ? 'text-[#3C3390]' : 'text-gray-500'">Paiement</span>
                    </div>
                </div>
            </div> -->
        </div>

        <!-- Container du formulaire avec header violet -->
        <div class="bg-white rounded-lg shadow-lg overflow-hidden">
            <!-- Header violet -->
            <div class="bg-[#3C3390] pt-8">
                <h2 class="text-white ps-4 pb-2 text-lg font-medium">{{ currentStepTitle }}</h2>
                <!-- Barre de progression -->
                <div class="mt-3 w-full bg-[#3C3390] bg-opacity-30 rounded-full h-2">
                    <div class="bg-[#2DA936] h-2 rounded-full transition-all duration-300"
                        :style="{ width: progressWidth }"></div>
                </div>
            </div>            <!-- Contenu du formulaire -->
            <div class="p-6">
                <!-- Étape 1: Identification du véhicule -->
                <VehiculeForm 
                    v-if="currentStep === 1"
                    :state="vehicleData" 
                    @submit="handleSubmit" 
                />
                
                <!-- Étape 2: Valeur du véhicule -->
                <ValeurForm 
                    v-else-if="currentStep === 2"
                    :state="valeurData"
                    :vehicle-data="vehicleData"
                    @submit="handleSubmit" 
                />
                
                <!-- Autres étapes à venir -->
                <div v-else class="text-center py-8">
                    <p class="text-gray-500">Étape {{ currentStep }} en cours de développement...</p>
                </div>
            </div>
        </div>
    </div>
    <div class="fixed bottom-0 left-0 right-0 bg-white shadow-lg p-4">
        <div class="flex justify-center items-center">
            <UButton @click="currentStep = Math.max(1, currentStep - 1)" label="Retour" icon="heroicons:arrow-left"
                class="px-4 py-2 border-2 bg-white text-[#2A2A7A] rounded-md hover:bg-white"
                :ui="{leadingIcon: 'pe-4'}" />
            <UButton @click="currentStep = Math.min(4, currentStep + 1)" label="Continuer"
                class="ml-4 px-8 py-2 bg-[#3C3390] text-white rounded-md hover:bg-[#2A2A7A] transition-colors" />
        </div>
    </div>
</template>
