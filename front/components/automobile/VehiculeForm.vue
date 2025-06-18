<script setup lang="ts">

// Props
interface Props {
    state: {
        imatriculationPart1: string
        imatriculationPart2: string
        imatriculationPart3: string
        marque: string
        modele: string
        puissance_fiscale: number
        numero_chassis: string
        date_mise_circulation: string
        places_assises: number
        carburation: string
    }
}

const props = defineProps<Props>()

// Events
defineEmits<{
    submit: [event: any]
}>()

// État de l'upload et du traitement
const isUploading = ref(false)
const uploadError = ref('')
const uploadSuccess = ref(false)

// Interface pour la réponse API
interface ApiResponse {
    numero_immatriculation?: string
    marque_vehicule?: string
    modele_vehicule?: string
    cylindree?: number
    numero_chassis?: string
    date_mise_circulation?: string
    nombre_places?: string
    carburation?: string
    extraction_confidence?: string
    error?: string
    suggestion?: string
}

// Fonction pour traiter le fichier uploadé
const handleFileUpload = async (event: Event) => {
    const target = event.target as HTMLInputElement
    const file = target.files?.[0]

    if (!file) return

    // Vérifier que c'est une image
    if (!file.type.startsWith('image/')) {
        uploadError.value = 'Veuillez sélectionner un fichier image'
        return
    }

    // Réinitialiser les états
    uploadError.value = ''
    uploadSuccess.value = false
    isUploading.value = true

    try {
        // Créer le FormData pour l'upload
        const formData = new FormData()
        formData.append('image', file)

        // Envoyer la requête à l'API (remplacez par votre URL d'API)
        const response = await fetch('http://localhost:8000/api/carte-grise/extract/', {
            method: 'POST',
            body: formData
        })

        const result: ApiResponse = await response.json()

        if (result.error) {
            // Gestion des erreurs
            uploadError.value = result.error
            if (result.suggestion) {
                uploadError.value += `. ${result.suggestion}`
            }
        } else {
            // Remplir automatiquement les champs
            fillFormFromApiResponse(result)
            uploadSuccess.value = true
        }

    } catch (error) {
        console.error('Erreur lors de l\'upload:', error)
        uploadError.value = 'Erreur lors du traitement de l\'image. Veuillez réessayer.'
    } finally {
        isUploading.value = false
    }
}

// Fonction pour remplir le formulaire avec la réponse API
const fillFormFromApiResponse = (response: ApiResponse) => {
    
    if (response.numero_immatriculation) {
        // Parser le numéro d'immatriculation
        // Format possible: "GE-107-EB" ou "GE107EB"
        let immat = response.numero_immatriculation
        
        if (immat.includes('-')) {
            // Format avec tirets: GE-107-EB
            const parts = immat.split('-')
            if (parts.length === 3) {
                props.state.imatriculationPart1 = parts[0]
                props.state.imatriculationPart2 = parts[1]
                props.state.imatriculationPart3 = parts[2]
            }
        } else {
            // Format sans tirets: GE107EB
            // Généralement: 2 lettres + chiffres + 2 lettres
            const match = immat.match(/^([A-Z]{2})(\d+)([A-Z]{2})$/)
            if (match) {
                props.state.imatriculationPart1 = match[1]
                props.state.imatriculationPart2 = match[2]
                props.state.imatriculationPart3 = match[3]
            } else {
                // Si le parsing échoue, mettre tout dans la partie centrale
                props.state.imatriculationPart1 = ''
                props.state.imatriculationPart2 = immat
                props.state.imatriculationPart3 = ''
            }
        }
    }
    
    if (response.marque_vehicule) {
        props.state.marque = response.marque_vehicule.trim()
    }
    
    if (response.modele_vehicule) {
        props.state.modele = response.modele_vehicule.trim()
    }
    
    if (response.cylindree && response.cylindree > 0) {
        // Convertir la cylindrée en puissance fiscale (approximation)
        props.state.puissance_fiscale = Math.round(response.cylindree / 100)
    } else {
        // Si pas de cylindrée, garder la valeur par défaut ou actuelle
        console.log('Pas de cylindrée fournie, puissance fiscale inchangée')
    }
    
    if (response.numero_chassis) {
        props.state.numero_chassis = response.numero_chassis.trim()
    }
    
    if (response.date_mise_circulation) {
        // Convertir le format de date (18/01/2022 -> 2022-01-18)
        const dateParts = response.date_mise_circulation.split('/')
        if (dateParts.length === 3) {
            const day = dateParts[0].padStart(2, '0')
            const month = dateParts[1].padStart(2, '0')
            const year = dateParts[2]
            props.state.date_mise_circulation = `${year}-${month}-${day}`
        }
    }
    
    if (response.nombre_places) {
        const places = parseInt(response.nombre_places)
        if (!isNaN(places) && places > 0) {
            props.state.places_assises = places
        }
    }
    
    if (response.carburation) {
        // Mapper les codes carburation vers les valeurs du select
        const carburationMap: Record<string, string> = {
            'EH': 'Hybride',
            'ES': 'Essence',
            'GO': 'Diesel',
            'EL': 'Électrique',
            'GP': 'GPL'
        }
        const mappedCarburation = carburationMap[response.carburation] || response.carburation
        props.state.carburation = mappedCarburation
    }
    
}

// Fonctions pour les compteurs
const incrementPuissance = () => {
    props.state.puissance_fiscale++
}

const decrementPuissance = () => {
    if (props.state.puissance_fiscale > 1) {
        props.state.puissance_fiscale--
    }
}

const incrementPlaces = () => {
    if (props.state.places_assises < 9) {
        props.state.places_assises++
    }
}

const decrementPlaces = () => {
    if (props.state.places_assises > 1) {
        props.state.places_assises--
    }
}

// Options pour les select
const vehicleModels = [
    'Yaris',
    'Corolla',
    'Camry',
    'Prius',
    'RAV4',
    'Highlander'
]

const fuelTypes = [
    'Essence',
    'Diesel',
    'Hybride',
    'Électrique',
    'GPL'
]

</script>

<template>
    <div>
        <UForm :state="props.state" @submit="$emit('submit', $event)"> <!-- Section upload de carte grise -->
            <div class="mb-8">
                <!-- Zone de drop pour l'image -->
                <div class="relative border-2 border-dashed rounded-lg p-8 text-center mb-4 transition-all duration-300"
                    :class="{
                        'border-[#2DA936] bg-gray-50': !isUploading && !uploadError && !uploadSuccess,
                        'border-blue-500 bg-blue-50': isUploading,
                        'border-red-500 bg-red-50': uploadError,
                        'border-green-500 bg-green-50': uploadSuccess
                    }">

                    <!-- Animation d'étoiles pendant le traitement -->
                    <div v-if="isUploading" class="absolute inset-0 pointer-events-none">
                        <div class="stars-animation">
                            <div class="star" v-for="i in 12" :key="i" :style="{
                                '--delay': i * 0.1 + 's',
                                '--duration': (1 + Math.random() * 0.5) + 's'
                            }">✨</div>
                        </div>
                    </div>

                    <div class="flex flex-col items-center relative z-10">
                        <!-- États différents selon le statut -->
                        <div v-if="!isUploading && !uploadError && !uploadSuccess">
                            <Icon name="i-heroicons-photo" class="min-h-20 min-w-20 text-[#2DA936] mb-3" />
                            <p class="text-gray-600 mb-2">Téléverser l'image de votre carte grise</p>
                            <input type="file" accept="image/*" @change="handleFileUpload" class="hidden"
                                id="file-upload" />
                            <label for="file-upload"
                                class="cursor-pointer inline-block px-4 py-2 bg-[#2DA936] text-white rounded-md hover:bg-green-600 transition-colors">
                                Choisir un fichier
                            </label>
                        </div>

                        <div v-else-if="isUploading" class="text-blue-600">
                            <Icon name="i-heroicons-cog-6-tooth" class="min-h-20 min-w-20 mb-3 animate-spin" />
                            <p class="font-medium">Traitement en cours...</p>
                            <p class="text-sm">L'IA analyse votre carte grise</p>
                        </div>

                        <div v-else-if="uploadError" class="text-red-600">
                            <Icon name="i-heroicons-exclamation-triangle" class="min-h-20 min-w-20 mb-3" />
                            <p class="font-medium">Erreur de traitement</p>
                            <p class="text-sm mb-3">{{ uploadError }}</p>
                            <button @click="uploadError = ''"
                                class="px-4 py-2 bg-red-500 text-white rounded-md hover:bg-red-600 transition-colors">
                                Réessayer
                            </button>
                        </div>

                        <div v-else-if="uploadSuccess" class="text-green-600">
                            <Icon name="i-heroicons-check-circle" class="min-h-20 min-w-20 mb-3" />
                            <p class="font-medium">Extraction réussie !</p>
                            <p class="text-sm mb-3">Les informations ont été automatiquement remplies</p>
                            <button @click="uploadSuccess = false; uploadError = ''"
                                class="px-4 py-2 bg-green-500 text-white rounded-md hover:bg-green-600 transition-colors">
                                Uploader une nouvelle image
                            </button>
                        </div>
                    </div>
                </div>

                <button type="button"
                    class="mx-auto flex items-center gap-2 px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-100 transition-colors"
                    :disabled="isUploading">
                    <Icon name="heroicons:camera" class="w-4 h-4" />
                    Capturer une image
                </button>
            </div>

            <div class="grid grid-cols-4">
                <div class="col-span-3">
                    <div class="mb-6">
                        <label class="block font-medium text-gray-700 mb-5">
                            Plaque d'immatriculation et votre numéro de châssis
                        </label>                        <div class="grid grid-cols-4 gap-2">
                            <CustomInput v-model="props.state.imatriculationPart1" placeholder="AA" maxlength="2"
                                class="col-span-1" />
                            <CustomInput v-model="props.state.imatriculationPart2" placeholder="555X" maxlength="4"
                                class="col-span-2" />
                            <CustomInput v-model="props.state.imatriculationPart3" placeholder="BB" maxlength="2"
                                class="col-span-1" />
                        </div>
                    </div>
                    <div class="mb-6">
                        <label class="block font-medium text-gray-700 mb-2">
                            Marque de véhicule
                        </label>
                        <CustomInput v-model="props.state.marque" class="w-full" placeholder="Toyota" />
                    </div>

                    <div class="mb-6">
                        <label class="block font-medium text-gray-700 mb-2">
                            Modèle du véhicule
                        </label>                        <CustomSelect v-model="props.state.modele" class="w-full" :items="vehicleModels"
                            placeholder="Sélectionner un modèle">
                            <template #trailing>
                                <Icon name="heroicons:chevron-down" class="w-4 h-4" />
                            </template>
                        </CustomSelect>
                    </div>
                    <div class="mb-6">
                        <label class="block font-medium text-gray-700 mb-2">
                            Puissance fiscale
                        </label>
                        <div class="flex items-center gap-4">
                            <button type="button" @click="decrementPuissance"
                                class="w-12 h-12 rounded-md border border-gray-300 flex items-center justify-center hover:bg-gray-100">
                                <Icon name="heroicons:minus" class="w-4 h-4" />
                            </button>
                            <CustomInput v-model="props.state.puissance_fiscale" class="w-[5rem]" />
                            <span class="text-gray-700 text-2xl font-semibold">CV</span>
                            <button type="button" @click="incrementPuissance"
                                class="w-12 h-12 rounded-md border border-gray-300 flex items-center justify-center hover:bg-gray-100">
                                <Icon name="heroicons:plus" class="w-4 h-4" />
                            </button>
                        </div>
                    </div>
                    <div class="mb-6">
                        <CustomInput v-model="props.state.numero_chassis" class="w-full" placeholder="Numéro châssis" />
                    </div>
                    <div class="mb-6">
                        <label class="block font-medium text-gray-700 mb-2">
                            Mise en circulation
                        </label>                        <CustomInput v-model="props.state.date_mise_circulation"
                            trailing-icon="i-heroicons-calendar-days-16-solid" class="w-full ps-56" type="date"
                            placeholder="09/07/2012" />
                    </div>
                    <div class="mb-6">
                        <label class="block font-medium text-gray-700 mb-2">
                            Nombre de place
                        </label>
                        <div class="flex items-center gap-4">
                            <button type="button" @click="decrementPlaces"
                                class="w-12 h-12 rounded-md border border-gray-300 flex items-center justify-center hover:bg-gray-100">
                                <Icon name="heroicons:minus" class="w-4 h-4" />
                            </button>
                            <CustomInput v-model="props.state.places_assises" class="w-[5rem]" />
                            <button type="button" @click="incrementPlaces"
                                class="w-12 h-12 rounded-md border border-gray-300 flex items-center justify-center hover:bg-gray-100">
                                <Icon name="heroicons:plus" class="w-4 h-4" />
                            </button>
                        </div>
                    </div>
                    <div class="mb-8">
                        <label class="block font-medium text-gray-700 mb-2">
                            Carburation
                        </label>                        <CustomSelect v-model="props.state.carburation" class="w-full" :items="fuelTypes"
                            placeholder="Essence">
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

<style scoped>
.stars-animation {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    overflow: hidden;
    pointer-events: none;
}

.star {
    position: absolute;
    font-size: 20px;
    animation: float var(--duration, 1.5s) ease-in-out infinite var(--delay, 0s);
    opacity: 0;
}

.star:nth-child(1) {
    top: 10%;
    left: 10%;
}

.star:nth-child(2) {
    top: 20%;
    left: 80%;
}

.star:nth-child(3) {
    top: 60%;
    left: 20%;
}

.star:nth-child(4) {
    top: 80%;
    left: 70%;
}

.star:nth-child(5) {
    top: 30%;
    left: 50%;
}

.star:nth-child(6) {
    top: 50%;
    left: 90%;
}

.star:nth-child(7) {
    top: 70%;
    left: 10%;
}

.star:nth-child(8) {
    top: 40%;
    left: 30%;
}

.star:nth-child(9) {
    top: 15%;
    left: 60%;
}

.star:nth-child(10) {
    top: 85%;
    left: 40%;
}

.star:nth-child(11) {
    top: 25%;
    left: 75%;
}

.star:nth-child(12) {
    top: 65%;
    left: 55%;
}

@keyframes float {

    0%,
    100% {
        opacity: 0;
        transform: translateY(0px) scale(0.8);
    }

    25% {
        opacity: 1;
        transform: translateY(-10px) scale(1.1);
    }

    50% {
        opacity: 1;
        transform: translateY(-5px) scale(1);
    }

    75% {
        opacity: 1;
        transform: translateY(-15px) scale(1.05);
    }
}

/* Animation de pulsation pour l'état de chargement */
.border-blue-500 {
    animation: pulse-border 1.5s ease-in-out infinite;
}

@keyframes pulse-border {

    0%,
    100% {
        border-color: rgb(59 130 246);
        box-shadow: 0 0 0 0 rgba(59, 130, 246, 0.4);
    }

    50% {
        border-color: rgb(37 99 235);
        box-shadow: 0 0 0 10px rgba(59, 130, 246, 0);
    }
}
</style>
