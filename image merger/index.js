//global variable
const imgs = []//save the loaded image 
let can_merge = true//check availability
let canvas_dataurl = null//merge result

//process the initial upload
document.querySelector('.custom_file_upload').addEventListener('click', (e) => {
    document.querySelector('.file_input').click()
})
document.querySelector('.file_input').addEventListener('change', async (e) => {
    if (e.target.files.length === 0) {
        return
    }
    console.log(e.target.files)

    //show loading，hide uploading
    document.querySelector('.area .loading').style['display'] = 'block';
    document.querySelector('.custom_file_upload').style['display'] = 'none';

    //traversal processing
    for (let file of e.target.files) {
        if (imgs.length < 6) {
            imgs.push(file);
        }
    }
    console.log(imgs)

    //preview
    const imgs_div = document.querySelectorAll('.img_')
    for (let i = 0; i < imgs.length; i++) {
        const reader = new FileReader();
        reader.readAsDataURL(imgs[i]);
        reader.onload = async function () {
            imgs_div[i].children[1].innerText = imgs[i].name
            imgs_div[i].style['display'] = 'block'
            const rect = imgs_div[i].children[0].getBoundingClientRect();
            const new_img = await resize_pre_show_img(reader.result, rect.width, rect.height)
            imgs_div[i].children[0].children[0].src = new_img.src
            imgs_div[i].children[0].children[0].width = new_img.width
            imgs_div[i].children[0].children[0].height = new_img.height

            //hide loading, show operation
            if (i === imgs.length - 1) {
                document.querySelector('.operation').style['display'] = 'flex'
                document.querySelector('.area .loading').style['display'] = 'none';
            }
        }
    }
})

//process add more
document.querySelector('.add_more').addEventListener('click', (e) => {
    document.querySelector('.add_more_input').click()
})
document.querySelector('.add_more_input').addEventListener('change', async (e) => {
    if (e.target.files.length === 0) {
        return
    }
    console.log(e.target.files)

    if (imgs.length >= 6) {
        alert('Cannot exceed 6 images!')
        return
    }

    //turn merge button into gray,change can_merge into false, turn add_more into loading
    document.querySelector('.merge').style['background-color'] = 'gray'
    can_merge = false;
    document.querySelector('.add_more p').innerText = 'Loading...'

    const idx = imgs.length - 1
    //traversal processing
    for (let file of e.target.files) {
        if (imgs.length < 6) {
            imgs.push(file);
        }
    }
    console.log(imgs)

    //preview
    const imgs_div = document.querySelectorAll('.img_')
    for (let i = idx; i < imgs.length; i++) {
        const reader = new FileReader();
        reader.readAsDataURL(imgs[i]);
        reader.onload = async function () {
            imgs_div[i].children[1].innerText = imgs[i].name
            imgs_div[i].style['display'] = 'block'
            const rect = imgs_div[i].children[0].getBoundingClientRect();
            const new_img = await resize_pre_show_img(reader.result, rect.width, rect.height)
            imgs_div[i].children[0].children[0].src = new_img.src
            imgs_div[i].children[0].children[0].width = new_img.width
            imgs_div[i].children[0].children[0].height = new_img.height

            //restore the merge button and status
            if (i === imgs.length - 1) {
                document.querySelector('.merge').style['background-color'] = '#705adc'
                can_merge = true
                document.querySelector('.add_more p').innerText = 'Add More'
            }
        }
    }
})

//prevew image and resize
const resize_pre_show_img = async (src, width, height) => {
    return new Promise((resolve, reject) => {
        let img = new Image()
        img.onload = () => {
            if (img.width >= img.height) {
                const ratio = img.height / img.width
                img.width = width
                img.height = width * ratio
                if (img.height > height) {
                    const ratio1 = img.width / img.height
                    img.height = height
                    img.width = height * ratio1
                }
            } else {
                const ratio = img.width / img.height
                img.height = height
                img.width = height * ratio
                if (img.width > width) {
                    const ratio1 = img.height / img.width
                    img.width = width
                    img.height = width * ratio
                }
            }

            return resolve(img)
        }
        img.onerror = reject
        img.src = src
    })
}

//process merging 
document.querySelector('.merge').addEventListener('click', async (e) => {
    if (can_merge !== true) {
        return
    }

    const direction_ele = document.querySelector('.select_direction select')
    const space_ele = document.querySelector('.input_space input')

    const direction = (direction_ele.value === 'vertical') ? 0 : 1
    const space = space_ele.value !== '' ? space_ele.value : 0
    let re = /^[\d]+$/;
    if (!re.test(space)) {
        alert('Space input error: please input integer!')
        return
    }
    console.log(`direction:${direction}`, `space:${space}`)
    await merge(direction, parseInt(space))
})

const get_img_helper = async (src) => {
    return new Promise((resolve, reject) => {
        let img = new Image()
        img.onload = () => resolve(img)
        img.onerror = reject
        img.src = src
    })
}

//obtain object from inputed file
const get_image = async (file) => {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.readAsDataURL(file);
        reader.onload = async function () {
            const img = get_img_helper(reader.result)
            return resolve(img)
        }
        reader.onerror = reject
    })
}

//create a merge function
const merge = async (direction, space) => {
    const images = []
    let new_images = null
    let canvas_height = 0
    let canvas_width = 0
    let canvas = document.createElement('canvas');
    let ctx = canvas.getContext('2d');

    //turn merge button into gray, turn add_more into loading
    document.querySelector('.merge').style['background-color'] = 'gray'
    can_merge = false
    document.querySelector('.add_more p').innerText = 'Processing...'

    //obtain the image object from the file object
    for (let i = 0; i < imgs.length; i++) {
        const img = await get_image(imgs[i])
        images.push(img)
        console.log(img.width, img.height)
    }

    //sort images by width or height based on landscape or vertical orientation
    let sorted_width_imgs = []
    let sorted_height_imgs = []
    if (direction === 0) {
        for (let i = 0; i < imgs.length; i++) {
            const img = await get_image(imgs[i])
            sorted_width_imgs.push(img)
        }
    } else {
        for (let i = 0; i < imgs.length; i++) {
            const img = await get_image(imgs[i])
            sorted_height_imgs.push(img)
        }
    }

    //get the maximum width or height from the sorted image and set the maximum width or height to the width or height of the canvas
    //the other dimension is the sum of the corresponding lengths of the aligned images plus the value of space
    
    //vertical
    if (direction === 0) {
        //sort by width
        sorted_width_imgs.sort((a, b) => b.width - a.width)
        const max_width = sorted_width_imgs[0].width
        //alignment width
        new_images = images.map((img, idx) => {
            const ratio = img.height / img.width
            img.width = max_width
            img.height = max_width * ratio
            return img
        })
        //calculate height
        for (let img of new_images) {
            canvas_height += img.height
        }
        canvas_width = max_width;
        canvas.height = canvas_height + space * (imgs.length - 1)
        canvas.width = canvas_width
    }

    //horizontal
    else {
        //sort by height
        sorted_height_imgs.sort((a, b) => b.height - a.height)
        const max_height = sorted_height_imgs[0].height
        //alignment height
        new_images = images.map((img, idx) => {
            const ratio = img.width / img.height
            img.height = max_height
            img.width = max_height * ratio
            return img
        })
        //calculate height
        for (let img of new_images) {
            canvas_width += img.width
        }
        canvas_height = max_height;
        canvas.height = canvas_height
        canvas.width = canvas_width + space * (imgs.length - 1)
    }

    console.log(canvas_width, canvas_height)

    //draw image
    let old_img = null
    let y = 0
    let x = 0
    for (let [idx, img] of new_images.entries()) {
        if (direction === 0) {
            if (old_img) {
                y += old_img.height
                //insert white
                if (space > 0) {
                    ctx.rect(0, y, canvas.width, space)
                    ctx.fillStyle = 'white'
                    ctx.fill()
                }
                y += space
            }
            ctx.drawImage(img, 0, y, img.width, img.height);
        } else {
            if (old_img) {
                x += old_img.width
                if (space > 0) {
                    //填充白色
                    ctx.rect(x, 0, space, canvas.height)
                    ctx.fillStyle = 'white'
                    ctx.fill()
                }
                x += space
            }
            ctx.drawImage(img, x, 0, img.width, img.height);
        }
        old_img = img
    }

    //control visual zone
    document.querySelector('.area').style['display'] = 'none'
    document.querySelector('.operation').style['display'] = 'none'
    const show_area = document.querySelector('.show_area')
    show_area.style['display'] = 'grid';
    if (direction === 0) {
        show_area.children[0].style['overflow-y'] = 'auto'
    } else {
        show_area.children[0].style['overflow-x'] = 'auto'
    }

    //convert Canvas to an image and display the image on the page
    canvas_dataurl = canvas.toDataURL('image/png');
    const img_container_rect = show_area.children[0].getBoundingClientRect();
    const img_ele = show_area.children[0].children[0]
    let img = await resize_show_img(canvas_dataurl, direction, img_container_rect.width, 500)
    // console.log(img_container_rect.width, img.height)
    // console.log(img.width, img.height)
    img_ele.src = img.src;
    img_ele.width = img.width * 0.9
    img_ele.height = img.height * 0.9

    //merge button restoration and status restoration
    document.querySelector('.merge').style['background-color'] = '#705adc'
    can_merge = true
    document.querySelector('.add_more p').innerText = 'Add More'
    document.querySelector('.continue').style['display'] = 'block'
}

const resize_show_img = async (src, direction, width, height) => {
    return new Promise((resolve, reject) => {
        let img = new Image()
        img.onload = () => {
            if (direction === 0) {
                const ratio = img.height / img.width
                img.width = width
                img.height = width * ratio
            } else {
                const ratio = img.width / img.height
                img.height = height
                img.width = height * ratio
            }

            return resolve(img)
        }
        img.onerror = reject
        img.src = src
    })
}

//download function
document.querySelector('.show_area .right button').addEventListener('click', async (e) => {
    if (canvas_dataurl === null) {
        return
    }

    const link = document.createElement("a");
    link.href = canvas_dataurl
    link.setAttribute("download", 'merged.png');
    document.body.appendChild(link)
    link.click();
    document.body.removeChild(link)

})

//initialize
document.querySelector('.continue').addEventListener('click', async (e) => {
    imgs.length = 0
    can_merge = true
    canvas_dataurl = null

    document.querySelector('.area').style['display'] = 'grid'
    document.querySelector('.custom_file_upload').style['display'] = 'block';
    const imgs_div = document.querySelectorAll('.img_')
    for (let i = 0; i < imgs_div.length; i++) {
        imgs_div[i].style['display'] = 'none'
    }

    document.querySelector('.operation').style['display'] = 'none'
    document.querySelector('.show_area').style['display'] = 'none'

    const direction_ele = document.querySelector('.select_direction select')
    const space_ele = document.querySelector('.input_space input')
    direction_ele.value='vertical'
    space_ele.value=''

})