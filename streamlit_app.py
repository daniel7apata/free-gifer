import streamlit as st
from PIL import Image
import io
from streamlit_sortables import sort_items

st.set_page_config(
    page_title="Creador de GIF",
    page_icon="✨",
    layout="centered"
)

st.title("✨ Creador de GIF a partir de PNGs")
st.markdown("Sube tus imágenes PNG, ordénalas arrastrándolas y crea tu GIF animado.")

# --- 1. Subida de archivos ---
uploaded_files = st.file_uploader(
    "📂 Sube tus imágenes en formato PNG",
    type="png",
    accept_multiple_files=True,
    help="Puedes seleccionar varios archivos a la vez."
)

if uploaded_files:
    # Creamos un diccionario para asociar el nombre de cada archivo con sus datos.
    file_map = {f.name: f for f in uploaded_files}
    
    # Creamos una lista solo con los NOMBRES de los archivos.
    filenames = list(file_map.keys())

    st.info("👇 **Arrastra y suelta los nombres de archivo para ordenarlos**.")

    # --- 2. Ordenamiento con Drag and Drop ---
    sorted_filenames = sort_items(filenames, multi_containers=False)

    # --- 3. Recuperar y mostrar imágenes en el nuevo orden ---
    ordered_files_data = [file_map[name] for name in sorted_filenames]

    st.markdown("### Orden Actual y Vista Previa")
    cols = st.columns(4)
    for i, file_data in enumerate(ordered_files_data):
        with cols[i % 4]:
            st.image(file_data, caption=f"#{i+1}: {file_data.name}", use_container_width=True)

    st.markdown("---")
    st.header("⚙️ Configuración del GIF")

    # --- 4. Opciones para el GIF ---
    st.markdown("#### Dimensiones del GIF")
    col_dim1, col_dim2 = st.columns(2)
    with col_dim1:
        width = st.number_input("↔️ Ancho (píxeles)", min_value=50, value=1000, step=50)
    with col_dim2:
        height = st.number_input("↕️ Alto (píxeles)", min_value=50, value=1000, step=50)

    st.markdown("#### Zoom y Recorte")
    zoom_factor = st.slider(
        "🔍 Factor de Zoom (x)",
        min_value=1.0,
        max_value=3.0,
        value=1.2,
        step=0.1,
        help="Aplica un zoom a la imagen y luego la recorta desde el centro."
    )

    st.markdown("#### Animación")
    col_anim1, col_anim2 = st.columns(2)
    with col_anim1:
        duration = st.slider(
            "⏱️ Duración por fotograma (ms)",
            min_value=50,
            max_value=2000,
            value=200,
            step=50,
            help="Milisegundos que dura cada imagen. Menos es más rápido."
        )
    with col_anim2:
        loop = st.checkbox("🔄 Repetir en bucle (infinito)", value=True)


    # --- 5. Botón para generar el GIF ---
    if st.button("🚀 Crear mi GIF", type="primary", use_container_width=True):
        with st.spinner("Creando GIF... ¡Esto puede tardar un momento!"):
            pil_images = []
            for img_data in ordered_files_data:
                img = Image.open(img_data)
                
                # Apply zoom and crop
                original_width, original_height = img.size
                
                # Calculate new dimensions after zoom
                zoomed_width = int(original_width * zoom_factor)
                zoomed_height = int(original_height * zoom_factor)

                # Resize image to the zoomed dimensions (this will make it larger)
                img = img.resize((zoomed_width, zoomed_height), Image.Resampling.LANCZOS)
                
                # Calculate crop box to get the center
                left = (zoomed_width - original_width) // 2
                top = (zoomed_height - original_height) // 2
                right = left + original_width
                bottom = top + original_height
                
                # Crop the image back to its original dimensions, effectively zooming in and cropping the center
                img = img.crop((left, top, right, bottom))
                
                pil_images.append(img)


            # Redimensionar cada imagen a las dimensiones especificadas (after zoom/crop)
            resized_images = [
                img.resize((width, height), Image.Resampling.LANCZOS) for img in pil_images
            ]

            # Crear el GIF en memoria usando las imágenes redimensionadas
            gif_buffer = io.BytesIO()
            resized_images[0].save(
                gif_buffer,
                format="GIF",
                save_all=True,
                append_images=resized_images[1:],
                duration=duration,
                loop=0 if loop else 1, # 0 para bucle infinito
                optimize=True
            )
            gif_buffer.seek(0)

        st.success("🎉 ¡Tu GIF está listo!")
        
        # --- 6. Mostrar y descargar el GIF ---
        st.image(gif_buffer)
        st.download_button(
            label="📥 Descargar GIF",
            data=gif_buffer,
            file_name=f"animacion_{width}x{height}.gif",
            mime="image/gif",
            use_container_width=True
        )
else:
    st.info("Aún no has subido ninguna imagen.")
