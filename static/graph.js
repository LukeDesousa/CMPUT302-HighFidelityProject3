(() => {
    const MIN_SCALE = 0.75;
    const MAX_SCALE = 2.6;
    const ZOOM_STEP = 0.18;
    const PAN_STEP = 28;

    const clamp = (value, min, max) => Math.min(max, Math.max(min, value));
    const distance = (pointA, pointB) => Math.hypot(pointA.x - pointB.x, pointA.y - pointB.y);
    const midpoint = (pointA, pointB) => ({
        x: (pointA.x + pointB.x) / 2,
        y: (pointA.y + pointB.y) / 2,
    });

    const workspaces = document.querySelectorAll("[data-graph-workspace]");

    workspaces.forEach((workspace) => {
        const viewport = workspace.querySelector("[data-graph-viewport]");
        const stage = workspace.querySelector("[data-graph-stage]");
        const graphLines = stage?.querySelectorAll(".graph-lines line") ?? [];
        const zoomValue = workspace.querySelector("[data-graph-zoom-value]");
        const zoomInButton = workspace.querySelector("[data-graph-zoom-in]");
        const zoomOutButton = workspace.querySelector("[data-graph-zoom-out]");
        const resetButton = workspace.querySelector("[data-graph-reset]");
        const defaultScale = clamp(
            Number.parseFloat(workspace.dataset.graphInitialScale || "1") || 1,
            MIN_SCALE,
            MAX_SCALE,
        );

        if (!viewport || !stage) {
            return;
        }

        const state = {
            scale: defaultScale,
            x: 0,
            y: 0,
            pointers: new Map(),
            drag: null,
            pinch: null,
            nodeDrag: null,
        };

        const clampPan = () => {
            const scaledWidth = stage.offsetWidth * state.scale;
            const scaledHeight = stage.offsetHeight * state.scale;
            const limitX = Math.max(24, (scaledWidth - viewport.clientWidth) / 2 + 24);
            const limitY = Math.max(24, (scaledHeight - viewport.clientHeight) / 2 + 24);

            state.x = clamp(state.x, -limitX, limitX);
            state.y = clamp(state.y, -limitY, limitY);
        };

        const applyTransform = (animate = false) => {
            clampPan();
            stage.style.transition = animate ? "transform 180ms ease" : "none";
            stage.style.transform = `translate(${state.x}px, ${state.y}px) scale(${state.scale})`;

            if (zoomValue) {
                zoomValue.textContent = `${Math.round(state.scale * 100)}%`;
            }
        };

        const zoomAt = (targetScale, clientX, clientY, animate = false) => {
            const nextScale = clamp(targetScale, MIN_SCALE, MAX_SCALE);
            if (nextScale === state.scale) {
                applyTransform(animate);
                return;
            }

            const rect = viewport.getBoundingClientRect();
            const focusX = (clientX ?? rect.left + rect.width / 2) - rect.left - rect.width / 2;
            const focusY = (clientY ?? rect.top + rect.height / 2) - rect.top - rect.height / 2;
            const ratio = nextScale / state.scale;

            state.x = focusX - ratio * (focusX - state.x);
            state.y = focusY - ratio * (focusY - state.y);
            state.scale = nextScale;
            applyTransform(animate);
        };

        const centerGraph = () => {
            state.scale = defaultScale;
            state.x = 0;
            state.y = 0;
            applyTransform(true);
        };

        const updatePointer = (event) => {
            state.pointers.set(event.pointerId, {x: event.clientX, y: event.clientY});
        };

        const clearPointer = (pointerId) => {
            state.pointers.delete(pointerId);
            viewport.classList.toggle("is-dragging", false);

            if (state.nodeDrag && state.nodeDrag.pointerId === pointerId) {
                state.nodeDrag = null;
            }

            if (state.pointers.size === 1) {
                const [[activePointerId, point]] = state.pointers.entries();
                state.drag = {
                    pointerId: activePointerId,
                    clientX: point.x,
                    clientY: point.y,
                    x: state.x,
                    y: state.y,
                };
                state.pinch = null;
                return;
            }

            state.drag = null;
            state.pinch = null;
        };

        viewport.addEventListener("wheel", (event) => {
            event.preventDefault();
            const scaleChange = event.deltaY < 0 ? 1 + ZOOM_STEP : 1 - ZOOM_STEP;
            zoomAt(state.scale * scaleChange, event.clientX, event.clientY);
        }, {passive: false});

        viewport.addEventListener("pointerdown", (event) => {
            const draggableNode = event.target.closest("[data-graph-node]");

            viewport.focus({preventScroll: true});
            viewport.setPointerCapture(event.pointerId);
            updatePointer(event);

            if (draggableNode && stage.contains(draggableNode)) {
                event.preventDefault();
                state.drag = null;
                state.pinch = null;
                state.nodeDrag = {
                    pointerId: event.pointerId,
                    node: draggableNode,
                    line: graphLines[Number.parseInt(draggableNode.dataset.graphLineIndex || "-1", 10)] || null,
                    clientX: event.clientX,
                    clientY: event.clientY,
                    left: Number.parseFloat(draggableNode.style.left || "50"),
                    top: Number.parseFloat(draggableNode.style.top || "50"),
                };
                viewport.classList.add("is-dragging");
                return;
            }

            if (state.pointers.size === 1) {
                state.drag = {
                    pointerId: event.pointerId,
                    clientX: event.clientX,
                    clientY: event.clientY,
                    x: state.x,
                    y: state.y,
                };
                viewport.classList.add("is-dragging");
            }

            if (state.pointers.size === 2) {
                const [pointA, pointB] = [...state.pointers.values()];
                state.drag = null;
                state.pinch = {
                    distance: distance(pointA, pointB),
                    midpoint: midpoint(pointA, pointB),
                };
                viewport.classList.remove("is-dragging");
            }
        });

        viewport.addEventListener("pointermove", (event) => {
            if (!state.pointers.has(event.pointerId)) {
                return;
            }

            updatePointer(event);

            if (state.nodeDrag && state.nodeDrag.pointerId === event.pointerId) {
                const scaledWidth = Math.max(stage.offsetWidth * state.scale, 1);
                const scaledHeight = Math.max(stage.offsetHeight * state.scale, 1);
                const deltaX = ((event.clientX - state.nodeDrag.clientX) / scaledWidth) * 100;
                const deltaY = ((event.clientY - state.nodeDrag.clientY) / scaledHeight) * 100;
                const nextLeft = clamp(state.nodeDrag.left + deltaX, 10, 90);
                const nextTop = clamp(state.nodeDrag.top + deltaY, 14, 90);

                state.nodeDrag.node.style.left = `${nextLeft}%`;
                state.nodeDrag.node.style.top = `${nextTop}%`;

                if (state.nodeDrag.line) {
                    state.nodeDrag.line.setAttribute("x2", nextLeft);
                    state.nodeDrag.line.setAttribute("y2", nextTop);
                }
                return;
            }

            if (state.pointers.size === 2 && state.pinch) {
                const [pointA, pointB] = [...state.pointers.values()];
                const nextDistance = distance(pointA, pointB);
                const nextMidpoint = midpoint(pointA, pointB);

                if (state.pinch.distance > 0) {
                    zoomAt(state.scale * (nextDistance / state.pinch.distance), nextMidpoint.x, nextMidpoint.y);
                    state.x += nextMidpoint.x - state.pinch.midpoint.x;
                    state.y += nextMidpoint.y - state.pinch.midpoint.y;
                    applyTransform();
                }

                state.pinch = {
                    distance: nextDistance,
                    midpoint: nextMidpoint,
                };
                return;
            }

            if (state.drag && state.drag.pointerId === event.pointerId) {
                state.x = state.drag.x + (event.clientX - state.drag.clientX);
                state.y = state.drag.y + (event.clientY - state.drag.clientY);
                applyTransform();
            }
        });

        ["pointerup", "pointercancel", "lostpointercapture"].forEach((eventName) => {
            viewport.addEventListener(eventName, (event) => {
                clearPointer(event.pointerId);
            });
        });

        viewport.addEventListener("keydown", (event) => {
            if (event.key === "+" || event.key === "=") {
                event.preventDefault();
                zoomAt(state.scale * (1 + ZOOM_STEP));
                return;
            }

            if (event.key === "-" || event.key === "_") {
                event.preventDefault();
                zoomAt(state.scale * (1 - ZOOM_STEP));
                return;
            }

            if (event.key === "0") {
                event.preventDefault();
                centerGraph();
                return;
            }

            if (event.key === "ArrowLeft") {
                event.preventDefault();
                state.x += PAN_STEP;
                applyTransform();
                return;
            }

            if (event.key === "ArrowRight") {
                event.preventDefault();
                state.x -= PAN_STEP;
                applyTransform();
                return;
            }

            if (event.key === "ArrowUp") {
                event.preventDefault();
                state.y += PAN_STEP;
                applyTransform();
                return;
            }

            if (event.key === "ArrowDown") {
                event.preventDefault();
                state.y -= PAN_STEP;
                applyTransform();
            }
        });

        zoomInButton?.addEventListener("click", () => zoomAt(state.scale * (1 + ZOOM_STEP), undefined, undefined, true));
        zoomOutButton?.addEventListener("click", () => zoomAt(state.scale * (1 - ZOOM_STEP), undefined, undefined, true));
        resetButton?.addEventListener("click", centerGraph);

        applyTransform();
    });
})();
